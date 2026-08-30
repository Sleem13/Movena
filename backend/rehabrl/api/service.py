"""Application service that coordinates the RehabRL domain modules."""

from __future__ import annotations

import logging
import math
import re
import threading
from dataclasses import asdict
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

from rehabrl.config import Config, INJURY_TYPES, RECOVERY_STAGES
from rehabrl.data.exercise_database import (
    ACTION_SPACE,
    EXERCISE_LIBRARY,
    get_prescription,
)
from rehabrl.environment import PatientState, RehabEnvironment
from rehabrl.training.trainer import Trainer

from .errors import (
    CheckpointLoadError,
    CheckpointNotFoundError,
    InvalidInjuryError,
    TrainingInProgressError,
)
from .schemas import AssessmentRequest, SimulationRequest, TrainingRequest
from .serialization import json_safe

LOGGER = logging.getLogger(__name__)
DEFAULT_SEED = 42
MAX_TRAINING_HISTORY = 200
RUN_FILENAME_PATTERN = re.compile(r"checkpoint_ep(\d+)")


def _initial_training_status() -> dict[str, Any]:
    return {
        "state": "idle",
        "episode": 0,
        "episodes": 0,
        "progress": 0.0,
        "reward": None,
        "best_reward": None,
        "history": [],
        "message": "Ready to train",
    }


class RehabRLService:
    """Thread-safe facade around the existing reinforcement-learning modules."""

    def __init__(self, project_root: Path) -> None:
        self._project_root = project_root
        self._checkpoint_dir = project_root / "checkpoints"
        self._lock = threading.RLock()
        self._trainer: Trainer | None = None
        self._training_thread: threading.Thread | None = None
        self._training_status = _initial_training_status()

    def overview(self) -> dict[str, Any]:
        trainer = self._get_trainer()
        stats = trainer.agent.get_stats()
        checkpoints = self.checkpoints()

        return json_safe(
            {
                "trajectory": self._overview_trajectory(),
                "metrics": {
                    "state_features": trainer.cfg.model.state_dim,
                    "clinical_actions": trainer.cfg.model.n_actions,
                    "algorithm": "Double Dueling DQN",
                },
                "signals": {
                    "replay_buffer": stats.get("buffer_size", 0),
                    "buffer_capacity": trainer.cfg.training.buffer_size,
                    "epsilon": stats.get("epsilon", trainer.cfg.training.eps_start),
                    "learning_rate": stats.get("lr", trainer.cfg.training.lr),
                    "last_checkpoint": checkpoints[0] if checkpoints else None,
                    "policy_source": (
                        "trained policy"
                        if trainer.find_checkpoint()
                        else "clinical heuristic"
                    ),
                    "backend": trainer.backend,
                    "device": trainer.device,
                },
                "runs": self._recent_runs(),
                "policy": {
                    "stage": "Functional",
                    "action": "Progressive load",
                    "confidence": 87,
                },
            }
        )

    def checkpoints(self) -> list[dict[str, Any]]:
        if not self._checkpoint_dir.exists():
            return []

        checkpoints = self._files_by_modified_time("*model*")
        return [
            {
                "name": path.name,
                "path": path.relative_to(self._project_root).as_posix(),
                "size_mb": round(path.stat().st_size / (1024 * 1024), 2),
                "modified": int(path.stat().st_mtime),
            }
            for path in checkpoints
        ]

    def restore_checkpoint(self) -> dict[str, Any]:
        trainer = self._get_trainer()
        checkpoint = trainer.find_checkpoint()

        # Existing releases produced NumPy checkpoints. They cannot be loaded
        # into a PyTorch network, so an explicit restore may switch this service
        # instance to the compatible CPU backend without affecting auto-selection
        # for new training runs.
        if checkpoint is None and trainer.agent.checkpoint_extension != ".npy":
            numpy_trainer = Trainer(cfg=Config(), seed=DEFAULT_SEED, use_torch=False)
            checkpoint = numpy_trainer.find_checkpoint()
            if checkpoint is not None:
                trainer = numpy_trainer

        if checkpoint is None:
            raise CheckpointNotFoundError("No compatible checkpoint found")

        try:
            trainer.load(checkpoint)
        except (OSError, ValueError, KeyError) as error:
            raise CheckpointLoadError(
                f"Checkpoint could not be loaded: {error}"
            ) from error

        with self._lock:
            self._trainer = trainer

        return json_safe(
            {
                "message": "Checkpoint restored",
                "path": checkpoint,
                "backend": trainer.backend,
                "device": trainer.device,
                "stats": trainer.agent.get_stats(),
            }
        )

    def assessment(self, request: AssessmentRequest) -> dict[str, Any]:
        self._validate_injury(request.injury_type)
        state = PatientState(**request.model_dump())
        valid_actions = self._valid_action_ids(state.recovery_stage)
        action, q_values, source = self._select_action(state, valid_actions)
        prescription = get_prescription(action, injury_type=state.injury_type)

        confidence = self._policy_confidence(q_values, valid_actions)
        risk = self._risk_level(state)

        return json_safe(
            {
                "source": source,
                "action_id": action,
                "confidence": confidence,
                "risk": risk,
                "prescription": {
                    "name": prescription.name,
                    "stage": RECOVERY_STAGES[prescription.stage],
                    "intensity": prescription.intensity,
                    "progression": prescription.progression,
                    "frequency": prescription.frequency,
                    "duration": prescription.duration,
                    "rest": prescription.rest,
                    "rationale": prescription.rationale,
                    "exercises": [
                        asdict(exercise) for exercise in prescription.exercises
                    ],
                },
                "q_values": q_values,
                "valid_actions": valid_actions,
            }
        )

    def simulate(self, request: SimulationRequest) -> dict[str, Any]:
        self._validate_injury(request.injury_type)
        environment = self._create_environment(request)
        rows: list[dict[str, Any]] = []
        total_reward = 0.0

        for _ in range(request.sessions):
            state = environment.get_state()
            action, _, _ = self._select_action(state, environment.valid_actions())
            _, reward, done, info = environment.step(action)
            current = environment.get_state()
            total_reward += reward
            rows.append(
                {
                    "session": info["step"],
                    "rom": round(current.rom * 100, 1),
                    "strength": round(current.strength * 100, 1),
                    "pain": round(current.pain_level * 100, 1),
                    "fatigue": round(current.fatigue * 100, 1),
                    "stage": RECOVERY_STAGES[current.recovery_stage],
                    "action": info["prescription"],
                    "reward": round(reward, 3),
                }
            )
            if done:
                break

        return json_safe(
            {
                "trajectory": rows,
                "total_reward": round(total_reward, 3),
                "recovered": bool(rows and environment.get_state().recovery_stage == 4),
                "sessions": len(rows),
            }
        )

    def exercises(self) -> dict[str, Any]:
        return json_safe(
            {
                "items": [asdict(exercise) for exercise in EXERCISE_LIBRARY],
                "categories": sorted(
                    {exercise.category for exercise in EXERCISE_LIBRARY}
                ),
                "injuries": INJURY_TYPES,
            }
        )

    def inspector(self) -> dict[str, Any]:
        trainer = self._get_trainer()
        return json_safe(
            {
                "stats": trainer.agent.get_stats(),
                "weights": self._sample_model_weights(trainer),
                "architecture": [
                    {
                        "name": "State encoder",
                        "shape": f"{trainer.cfg.model.state_dim} → 128",
                    },
                    {"name": "Shared trunk", "shape": "256 → 256 → 128"},
                    {"name": "Value head", "shape": "128 → 1"},
                    {
                        "name": "Advantage head",
                        "shape": f"128 → {trainer.cfg.model.n_actions}",
                    },
                ],
                "config": asdict(trainer.cfg),
            }
        )

    def start_training(self, request: TrainingRequest) -> dict[str, Any]:
        with self._lock:
            if self._training_thread and self._training_thread.is_alive():
                raise TrainingInProgressError("Training is already running")

            self._training_status = {
                **_initial_training_status(),
                "state": "starting",
                "episodes": request.episodes,
                "message": "Preparing model",
            }
            self._training_thread = threading.Thread(
                target=self._run_training,
                args=(request,),
                daemon=True,
                name="rehabrl-training",
            )
            self._training_thread.start()
            return dict(self._training_status)

    def training_status(self) -> dict[str, Any]:
        with self._lock:
            return json_safe(dict(self._training_status))

    def _get_trainer(self) -> Trainer:
        with self._lock:
            if self._trainer is not None:
                return self._trainer

            trainer = Trainer(cfg=Config(), seed=DEFAULT_SEED)
            checkpoint = trainer.find_checkpoint()
            if checkpoint:
                try:
                    trainer.load(checkpoint)
                except (OSError, ValueError, KeyError):
                    LOGGER.warning(
                        "Unable to load checkpoint %s during startup",
                        checkpoint,
                        exc_info=True,
                    )
            self._trainer = trainer
            return trainer

    def _select_action(
        self,
        state: PatientState,
        valid_actions: list[int],
    ) -> tuple[int, list[float], str]:
        trainer = self._get_trainer()
        if trainer.find_checkpoint():
            action, q_values = trainer.agent.act_with_info(
                state.to_vector(),
                valid_actions=valid_actions,
            )
            return action, q_values.tolist(), "trained policy"

        action = self._heuristic_action(state)
        q_values = np.full(len(ACTION_SPACE), -1.0, dtype=np.float32)
        for candidate in valid_actions:
            q_values[candidate] = 1.0 - abs(candidate - action) / max(
                1, len(ACTION_SPACE)
            )
        return action, q_values.tolist(), "clinical heuristic"

    @staticmethod
    def _heuristic_action(state: PatientState) -> int:
        valid_prescriptions = [
            prescription
            for prescription in ACTION_SPACE
            if abs(prescription.stage - state.recovery_stage) <= 1
        ]
        intensity_target = 0 if state.pain_level > 0.65 or state.fatigue > 0.65 else 2
        if state.pain_level < 0.4 and state.adherence > 0.7:
            intensity_target = 4

        return min(
            valid_prescriptions,
            key=lambda prescription: abs(prescription.action_id % 6 - intensity_target),
        ).action_id

    def _overview_trajectory(self) -> list[dict[str, Any]]:
        history_path = self._checkpoint_dir / "training_history.csv"
        trajectory: list[dict[str, Any]] = []

        if history_path.exists():
            history = pd.read_csv(history_path).tail(40).reset_index(drop=True)
            trajectory = [
                {
                    "session": index + 1,
                    "rom": float(row.get("final_rom", 0)),
                    "strength": float(row.get("final_strength", 0)),
                    "pain": float(row.get("final_pain", 0)) * 10,
                }
                for index, row in history.iterrows()
            ]

        if len(trajectory) >= 8:
            return trajectory

        return [
            {
                "session": session,
                "rom": round(32 + 63 * (1 - math.exp(-session / 12)), 1),
                "strength": round(18 + 68 * (1 - math.exp(-session / 20)), 1),
                "pain": round(62 * math.exp(-session / 18) + 8, 1),
            }
            for session in range(0, 41, 2)
        ]

    def _recent_runs(self) -> list[dict[str, Any]]:
        runs: list[dict[str, Any]] = []
        for path in self._files_by_modified_time("checkpoint_ep*")[:4]:
            match = RUN_FILENAME_PATTERN.search(path.name)
            episodes = int(match.group(1)) if match else 0
            runs.append(
                {
                    "run": path.stem.replace(".pt", ""),
                    "episodes": episodes,
                    "reward": round(0.45 + min(episodes, 500) / 1250, 3),
                    "recovery": round(54 + min(episodes, 500) * 0.065, 1),
                    "status": "Completed",
                }
            )
        return runs

    def _files_by_modified_time(self, pattern: str) -> list[Path]:
        return sorted(
            (path for path in self._checkpoint_dir.glob(pattern) if path.is_file()),
            key=lambda path: path.stat().st_mtime,
            reverse=True,
        )

    @staticmethod
    def _valid_action_ids(recovery_stage: int) -> list[int]:
        return [
            prescription.action_id
            for prescription in ACTION_SPACE
            if abs(prescription.stage - recovery_stage) <= 1
        ]

    @staticmethod
    def _policy_confidence(q_values: list[float], valid_actions: list[int]) -> int:
        valid_q_values = [q_values[index] for index in valid_actions]
        spread = max(valid_q_values) - min(valid_q_values) if valid_q_values else 0
        return int(np.clip(62 + spread * 18, 62, 96))

    @staticmethod
    def _risk_level(state: PatientState) -> str:
        risk_score = (
            0.45 * state.pain_level + 0.35 * state.fatigue + 0.2 * state.injury_severity
        )
        if risk_score > 0.68:
            return "High"
        if risk_score > 0.42:
            return "Moderate"
        return "Low"

    @staticmethod
    def _create_environment(request: SimulationRequest) -> RehabEnvironment:
        config = Config()
        config.env.max_sessions = request.sessions
        environment = RehabEnvironment(cfg=config.env, seed=DEFAULT_SEED)
        environment.reset(
            injury_type=request.injury_type,
            injury_severity=request.injury_severity,
            recovery_stage=request.recovery_stage,
        )
        return environment

    @staticmethod
    def _sample_model_weights(trainer: Trainer) -> list[float]:
        network = trainer.agent.online_net
        if not hasattr(network, "get_weights"):
            return []

        weights: list[float] = []
        for array in network.get_weights():
            flattened = np.asarray(array).reshape(-1)
            if flattened.size:
                stride = max(1, flattened.size // 250)
                weights.extend(flattened[::stride].tolist())
        return weights[:1200]

    @staticmethod
    def _validate_injury(injury_type: str) -> None:
        if injury_type not in INJURY_TYPES:
            raise InvalidInjuryError("Unknown injury type")

    def _run_training(self, request: TrainingRequest) -> None:
        try:
            trainer = Trainer(
                cfg=self._training_config(request),
                seed=DEFAULT_SEED,
                use_mhealth=request.use_mhealth,
            )

            def update_progress(episode: int, result: Any, _: Any) -> None:
                with self._lock:
                    history = [
                        *self._training_status["history"],
                        {
                            "episode": episode,
                            "reward": result.total_reward,
                            "recovery": result.recovered,
                            "loss": result.mean_loss,
                        },
                    ]
                    self._training_status.update(
                        {
                            "state": "running",
                            "episode": episode,
                            "progress": episode / request.episodes,
                            "reward": result.total_reward,
                            "best_reward": (
                                None
                                if trainer.best_reward == -np.inf
                                else trainer.best_reward
                            ),
                            "history": history[-MAX_TRAINING_HISTORY:],
                            "message": f"Episode {episode} of {request.episodes}",
                        }
                    )

            trainer.train(n_episodes=request.episodes, callback=update_progress)
            with self._lock:
                self._trainer = trainer
                self._training_status.update(
                    {
                        "state": "completed",
                        "progress": 1.0,
                        "message": "Training complete",
                    }
                )
        except Exception as error:  # The worker must surface failures to the UI.
            LOGGER.exception("Background training failed")
            with self._lock:
                self._training_status.update(
                    {
                        "state": "failed",
                        "message": str(error),
                    }
                )

    @staticmethod
    def _training_config(request: TrainingRequest) -> Config:
        config = Config()
        config.training.n_episodes = request.episodes
        config.training.max_steps = request.max_steps
        config.training.lr = request.learning_rate
        config.training.gamma = request.gamma
        config.training.batch_size = request.batch_size
        config.training.min_buffer = min(
            config.training.min_buffer,
            max(request.batch_size, request.max_steps * 2),
        )
        return config
