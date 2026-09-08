"""
rehab_rl/training/trainer.py
Training loop, evaluation, and logging for the Rehabilitation DQN agent.
"""

import os
import numpy as np
import pandas as pd
from dataclasses import dataclass, field
from typing import List, Optional, Callable, Dict, Tuple

from rehabrl.config import Config, INJURY_TYPES
from rehabrl.environment import RehabEnvironment

try:
    from rehabrl.agents.dqn_agent import DQNAgent, cuda_is_available

    TORCH_AVAILABLE = True
except ImportError:
    TORCH_AVAILABLE = False
from rehabrl.agents.numpy_agent import NumpyDQNAgent
from rehabrl.data.exercise_ref import (
    build_action_priors,
    load_exercise_refs,
    summarize_entries,
)


# ─── Metrics ────────────────────────────────────────────────────────────────────


@dataclass
class EpisodeResult:
    episode: int
    total_reward: float
    steps: int
    recovered: bool
    final_rom: float
    final_strength: float
    final_pain: float
    final_stage: int
    epsilon: float
    mean_loss: float


@dataclass
class TrainingHistory:
    episodes: List[EpisodeResult] = field(default_factory=list)

    def append(self, r: EpisodeResult):
        self.episodes.append(r)

    def to_dataframe(self) -> pd.DataFrame:
        return pd.DataFrame([e.__dict__ for e in self.episodes])

    def recent_mean_reward(self, n: int = 20) -> float:
        recent = self.episodes[-n:]
        return float(np.mean([e.total_reward for e in recent])) if recent else 0.0

    def recovery_rate(self, n: int = 20) -> float:
        recent = self.episodes[-n:]
        return float(np.mean([e.recovered for e in recent])) if recent else 0.0


# ─── Trainer ────────────────────────────────────────────────────────────────────


class Trainer:
    """
    Manages the full training loop for the DQN rehabilitation agent.

    Usage:
        trainer = Trainer(cfg)
        history = trainer.train(n_episodes=500, callback=my_callback)
        trainer.save("checkpoints/model.pt")
    """

    def __init__(
        self,
        cfg: Optional[Config] = None,
        device: Optional[str] = None,
        seed: int = 42,
        use_torch: Optional[bool] = None,
        use_mhealth: bool = False,  # Use mHealth dataset
        exercise_ref_dir: Optional[str] = None,
        exercise_ref_strength: float = 0.2,  # guidance strength from exercise references
        movena_data_dir: Optional[str] = None,
    ):
        self.cfg = cfg or Config()
        self.env = RehabEnvironment(
            cfg=self.cfg.env,
            seed=seed,
            use_mhealth=use_mhealth,
            movena_data_dir=movena_data_dir,
        )
        self.rng = np.random.default_rng(seed)

        self.exercise_refs = []
        self.exercise_ref_priors = None
        self.exercise_ref_condition_priors = {}
        self.exercise_ref_condition_stage_priors: Dict[
            Tuple[Optional[str], Optional[int]], List[float]
        ] = {}
        self.exercise_ref_strength = exercise_ref_strength
        if exercise_ref_dir:
            try:
                self.exercise_refs = load_exercise_refs(exercise_ref_dir)
                self.exercise_ref_priors = build_action_priors(self.exercise_refs)
                self.exercise_ref_condition_priors = {
                    injury: build_action_priors(
                        self.exercise_refs, preferred_condition=injury
                    )
                    for injury in INJURY_TYPES
                }
                print(summarize_entries(self.exercise_refs))
            except Exception:
                self.exercise_refs = []
                self.exercise_ref_priors = None
                self.exercise_ref_condition_priors = {}
                self.exercise_ref_condition_stage_priors = {}

        # Automatic mode uses CUDA when available and the NumPy CPU backend
        # otherwise, preserving compatibility with existing NumPy checkpoints.
        if use_torch is None:
            use_torch = TORCH_AVAILABLE and cuda_is_available()
        elif use_torch and not TORCH_AVAILABLE:
            raise RuntimeError("PyTorch was requested but is not installed")

        if use_torch:
            selected_device = device or self.cfg.device
            self.agent = DQNAgent(cfg=self.cfg, device=selected_device)
        else:
            self.agent = NumpyDQNAgent(cfg=self.cfg, seed=seed)

        stats = self.agent.get_stats()
        self.backend = stats["backend"]
        self.device = stats["device"]

        self.history = TrainingHistory()
        self.best_reward = -np.inf
        self.save_dir = self.cfg.save_dir

    def _exercise_ref_action_weights(
        self,
        valid_actions,
        preferred_condition: Optional[str] = None,
        recovery_stage: Optional[int] = None,
    ):
        if self.exercise_ref_priors is None or valid_actions is None:
            return np.ones(self.env.n_actions, dtype=np.float32)

        priors = self.exercise_ref_priors
        cache_key = (preferred_condition, recovery_stage)
        if preferred_condition or recovery_stage is not None:
            priors = self.exercise_ref_condition_stage_priors.get(cache_key)
            if priors is None:
                priors = build_action_priors(
                    self.exercise_refs,
                    preferred_condition=preferred_condition,
                    recovery_stage=recovery_stage,
                )
                self.exercise_ref_condition_stage_priors[cache_key] = priors

        weights = np.zeros(self.env.n_actions, dtype=np.float32)
        for a in valid_actions:
            if 0 <= a < len(priors):
                weights[a] = priors[a]
        if weights.sum() <= 0:
            weights[valid_actions] = 1.0
        return weights / max(1.0, weights.sum())

    def _select_exercise_ref_guidance(
        self,
        valid_actions,
        preferred_condition: Optional[str] = None,
        recovery_stage: Optional[int] = None,
    ):
        weights = self._exercise_ref_action_weights(
            valid_actions,
            preferred_condition=preferred_condition,
            recovery_stage=recovery_stage,
        )
        valid_weights = weights[valid_actions]
        if valid_weights.sum() <= 0:
            return int(self.rng.choice(valid_actions))
        normalized = valid_weights / valid_weights.sum()
        return int(self.rng.choice(valid_actions, p=normalized))

    def _select_action(self, state, valid_actions, training: bool = True):
        if self.exercise_ref_priors is None or self.exercise_ref_strength <= 0.0:
            return self.agent.act(state, valid_actions=valid_actions, training=training)

        preferred_condition = (
            self.env.get_state().injury_type if hasattr(self.env, "get_state") else None
        )
        recovery_stage = (
            self.env.get_state().recovery_stage
            if hasattr(self.env, "get_state")
            else None
        )
        if training and self.rng.random() < self.agent.epsilon:
            return self._select_exercise_ref_guidance(
                valid_actions,
                preferred_condition=preferred_condition,
                recovery_stage=recovery_stage,
            )

        if hasattr(self.agent, "act_with_info"):
            action, q_vals = self.agent.act_with_info(
                state, valid_actions=valid_actions
            )
        else:
            return self.agent.act(state, valid_actions=valid_actions, training=training)

        prior = self._exercise_ref_action_weights(
            valid_actions,
            preferred_condition=preferred_condition,
            recovery_stage=recovery_stage,
        )
        adjusted = q_vals.astype(np.float32).copy()
        adjusted[valid_actions] = q_vals[
            valid_actions
        ] + self.exercise_ref_strength * np.log(prior[valid_actions] + 1e-8)
        return int(np.argmax(adjusted))

    def pretrain_from_exercise_refs(
        self,
        n_steps: int = 200,
        max_episode_steps: int = 20,
    ) -> int:
        """Seed replay with exercise-ref-guided transitions."""
        if not self.exercise_refs or self.exercise_ref_priors is None:
            return 0

        step_count = 0
        episode_steps = 0
        state = self.env.reset()

        while step_count < n_steps:
            preferred_condition = (
                self.env.get_state().injury_type
                if hasattr(self.env, "get_state")
                else None
            )
            valid = self.env.valid_actions()
            action = self._select_exercise_ref_guidance(
                valid, preferred_condition=preferred_condition
            )
            next_state, reward, done, info = self.env.step(action)

            self.agent.remember(state, action, reward, next_state, done)
            if self.agent.buffer.is_ready:
                self.agent.learn()

            state = next_state
            step_count += 1
            episode_steps += 1

            if done or episode_steps >= max_episode_steps:
                episode_steps = 0
                injury_type = (
                    self.rng.choice(list(self.exercise_ref_condition_priors.keys()))
                    if self.exercise_ref_condition_priors
                    else None
                )
                recovery_stage = int(self.rng.integers(0, 5))
                state = self.env.reset(
                    injury_type=injury_type, recovery_stage=recovery_stage
                )

        return step_count

    def _run_episode(self, training: bool = True) -> EpisodeResult:
        """Run a single episode. Returns episode metrics."""
        state = self.env.reset()
        total_reward = 0.0
        step_losses = []

        for step in range(self.cfg.training.max_steps):
            valid = self.env.valid_actions()
            action = self._select_action(state, valid_actions=valid, training=training)
            next_state, reward, done, info = self.env.step(action)

            if training:
                self.agent.remember(state, action, reward, next_state, done)
                loss = self.agent.learn()
                if loss is not None:
                    step_losses.append(loss)

            state = next_state
            total_reward += reward

            if done:
                break

        if training:
            self.agent.end_episode()

        ps = self.env.get_state()
        return EpisodeResult(
            episode=self.agent.episodes,
            total_reward=round(total_reward, 3),
            steps=step + 1,
            recovered=info.get("recovered", False),
            final_rom=round(ps.rom * 100, 1),
            final_strength=round(ps.strength * 100, 1),
            final_pain=round(ps.pain_level * 10, 1),
            final_stage=ps.recovery_stage,
            epsilon=round(self.agent.epsilon, 4),
            mean_loss=round(float(np.mean(step_losses)), 5) if step_losses else 0.0,
        )

    def train(
        self,
        n_episodes: int = 500,
        checkpoint_name: str = "best_model",
        callback: Optional[
            Callable[[int, EpisodeResult, TrainingHistory], None]
        ] = None,
    ) -> TrainingHistory:
        """
        Main training loop.
        callback(episode, result, history) is called every episode — use for Streamlit progress.
        """
        tcfg = self.cfg.training
        os.makedirs(self.save_dir, exist_ok=True)

        for ep in range(1, n_episodes + 1):
            result = self._run_episode(training=True)
            self.history.append(result)

            # Save best model
            if (
                result.total_reward > self.best_reward
                and len(self.agent.buffer) > tcfg.min_buffer
            ):
                self.best_reward = result.total_reward
                self.save(self.checkpoint_path(checkpoint_name))

            # Periodic checkpoint
            if ep % 50 == 0:
                self.save(self.checkpoint_path(f"checkpoint_ep{ep}"))

            if callback:
                callback(ep, result, self.history)

        return self.history

    def evaluate(self, n_episodes: int = 20) -> Dict:
        """Run evaluation episodes (no exploration, no learning)."""
        results = []
        for _ in range(n_episodes):
            r = self._run_episode(training=False)
            results.append(r)

        df = pd.DataFrame([r.__dict__ for r in results])
        return {
            "mean_reward": round(float(df.total_reward.mean()), 3),
            "std_reward": round(float(df.total_reward.std()), 3),
            "recovery_rate": round(float(df.recovered.mean()), 3),
            "mean_steps": round(float(df.steps.mean()), 1),
            "mean_rom": round(float(df.final_rom.mean()), 1),
            "mean_strength": round(float(df.final_strength.mean()), 1),
            "mean_pain": round(float(df.final_pain.mean()), 1),
        }

    def simulate_trajectory(
        self,
        injury_type: Optional[str] = None,
        injury_severity: float = 0.7,
        recovery_stage: int = 0,
    ) -> pd.DataFrame:
        """
        Simulate a full recovery trajectory using the trained greedy policy.
        Returns a DataFrame with per-session metrics.
        """
        state = self.env.reset(
            injury_type=injury_type,
            injury_severity=injury_severity,
            recovery_stage=recovery_stage,
        )
        for _ in range(self.cfg.training.max_steps):
            valid = self.env.valid_actions()
            action = self.agent.act(state, valid_actions=valid, training=False)
            state, _, done, _ = self.env.step(action)
            if done:
                break
        return self.env.get_trajectory()

    def save(self, path: str):
        self.agent.save(path)

    def load(self, path: str):
        self.agent.load(path)

    def checkpoint_path(self, name: str = "best_model") -> str:
        """Return the canonical checkpoint path for the active agent backend."""
        extension = self.agent.checkpoint_extension
        return os.path.join(self.save_dir, f"{name}{extension}")

    def find_checkpoint(self, name: str = "best_model") -> Optional[str]:
        """Find a current checkpoint, including legacy NumPy ``.pt.npy`` files."""
        candidates = [self.checkpoint_path(name)]
        if self.agent.checkpoint_extension == ".npy":
            candidates.append(os.path.join(self.save_dir, f"{name}.pt.npy"))

        return next((path for path in candidates if os.path.isfile(path)), None)


# ─── Baseline: Random Policy ────────────────────────────────────────────────────


class RandomPolicy:
    """Samples uniform random actions — used as a baseline comparison."""

    def __init__(self, n_actions: int):
        self.n_actions = n_actions

    def act(self, state: np.ndarray, valid_actions=None, **kwargs) -> int:
        if valid_actions:
            return int(np.random.choice(valid_actions))
        return int(np.random.randint(self.n_actions))


def compare_policies(cfg: Optional[Config] = None, n_episodes: int = 30) -> Dict:
    """Quick comparison between trained DQN and random baseline."""
    cfg = cfg or Config()

    def evaluate_policy(policy, env, n=n_episodes):
        rewards = []
        for _ in range(n):
            state = env.reset()
            total = 0.0
            for _ in range(cfg.training.max_steps):
                valid = env.valid_actions()
                action = policy.act(state, valid_actions=valid, training=False)
                state, r, done, _ = env.step(action)
                total += r
                if done:
                    break
            rewards.append(total)
        return float(np.mean(rewards)), float(np.std(rewards))

    env = RehabEnvironment(cfg=cfg.env)
    rng_m, rng_s = evaluate_policy(RandomPolicy(cfg.model.n_actions), env)
    return {"random_mean": round(rng_m, 3), "random_std": round(rng_s, 3)}
