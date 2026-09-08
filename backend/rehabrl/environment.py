"""
rehab_rl/environment.py
Rehabilitation RL Environment.

Models the recovery process as a Markov Decision Process:
  State  S  →  patient metrics vector (dim 28)
  Action A  →  one of 30 discrete prescription templates
  Reward R  →  weighted composite of clinical outcomes
  Policy π  →  learned by the DQN agent

Optionally uses real mHealth sensor data for more realistic patient modeling.
"""

import numpy as np
from dataclasses import dataclass, field
from typing import Tuple, Dict, Optional, List
import os

from rehabrl.config import (
    INJURY_TYPES,
    MHEALTH_DATA_DIR,
    N_ACTIONS,
    RECOVERY_STAGES,
    STATE_DIM,
    EnvConfig,
)
from rehabrl.data.exercise_database import ACTION_SPACE, get_prescription
from rehabrl.data.rehab24_loader import Rehab246Loader, Rehab246Profile

# Try to import mHealth loader if available
try:
    from rehabrl.data.mhealth_loader import MHealthLoader, activity_to_rehab_metrics

    MHEALTH_AVAILABLE = True
except ImportError:
    MHEALTH_AVAILABLE = False


# ─── Patient State ─────────────────────────────────────────────────────────────


@dataclass
class PatientState:
    """Human-readable patient state representation."""

    injury_type: str = "ACL Tear"
    injury_severity: float = 0.7  # 0–1 (1 = most severe)
    recovery_stage: int = 0  # 0=Acute … 4=Return
    pain_level: float = 0.6  # 0–1 (1 = worst pain)
    rom: float = 0.6  # Range-of-motion 0–1
    strength: float = 0.5  # Strength 0–1
    movement_quality: float = 0.5  # Movement quality 0–1
    fatigue: float = 0.3  # Fatigue 0–1
    adherence: float = 0.85  # Session adherence rate 0–1
    days_since: float = 1.0  # Days since last session (normalised /14)
    session_number: int = 1
    joint_angles: np.ndarray = field(default_factory=lambda: np.zeros(6))

    def to_vector(self) -> np.ndarray:
        """Encode state as a 28-dim float32 vector."""
        # One-hot injury type (12)
        inj_oh = np.zeros(len(INJURY_TYPES), dtype=np.float32)
        try:
            inj_oh[INJURY_TYPES.index(self.injury_type)] = 1.0
        except ValueError:
            inj_oh[0] = 1.0

        # One-hot recovery stage (5)
        stage_oh = np.zeros(len(RECOVERY_STAGES), dtype=np.float32)
        stage_oh[min(4, max(0, self.recovery_stage))] = 1.0

        # Continuous metrics (9)
        continuous = np.array(
            [
                self.pain_level,
                self.rom,
                self.strength,
                self.movement_quality,
                self.fatigue,
                self.adherence,
                min(1.0, self.days_since / 14.0),
                min(1.0, self.session_number / 50.0),
                self.injury_severity,
            ],
            dtype=np.float32,
        )

        return np.concatenate([inj_oh, stage_oh, continuous, self.joint_angles]).astype(
            np.float32
        )  # shape (32,)

    def summary(self) -> Dict:
        return {
            "injury": self.injury_type,
            "stage": RECOVERY_STAGES[self.recovery_stage],
            "pain": round(self.pain_level * 10, 1),
            "rom_pct": round(self.rom * 100, 1),
            "str_pct": round(self.strength * 100, 1),
            "mov_qual": round(self.movement_quality * 10, 1),
            "fatigue": round(self.fatigue * 10, 1),
            "adherence": round(self.adherence * 100, 1),
        }

    def clone(self) -> "PatientState":
        return PatientState(**self.__dict__)


# ─── Reward Function ────────────────────────────────────────────────────────────


class RewardFunction:
    """
    Multi-component reward signal:
      R = w_pain * ΔPain  +  w_rom * ΔROM  +  w_strength * ΔStrength
        + w_adherence * Adherence  -  w_safety * SafetyPenalty

    Positive: metric improvements and good adherence.
    Negative: pain spikes, overtraining, non-compliance.
    """

    def __init__(self, cfg: EnvConfig):
        self.cfg = cfg

    def compute(
        self,
        prev: PatientState,
        curr: PatientState,
        action_id: int,
        overtraining: bool = False,
    ) -> Tuple[float, Dict]:
        prescription = get_prescription(action_id)

        # ── Pain component (negative pain is good) ──────────────────────
        delta_pain = prev.pain_level - curr.pain_level  # positive if improved
        r_pain = np.clip(delta_pain * 3.0, -1.0, 1.0)

        # ── ROM component ────────────────────────────────────────────────
        delta_rom = curr.rom - prev.rom
        r_rom = np.clip(delta_rom * 3.0, -1.0, 1.0)

        # ── Strength component ───────────────────────────────────────────
        delta_str = curr.strength - prev.strength
        r_strength = np.clip(delta_str * 3.0, -1.0, 1.0)

        # ── Adherence bonus ──────────────────────────────────────────────
        r_adherence = curr.adherence  # already 0–1

        # ── Safety penalty ───────────────────────────────────────────────
        safety_penalty = 0.0
        if overtraining:
            safety_penalty += 0.5
        if curr.pain_level > 0.8:  # pain too high
            safety_penalty += 0.3
        # Prescribing high-intensity in acute stage is unsafe
        if prescription.stage > curr.recovery_stage + 1:
            safety_penalty += 0.4
        if prescription.intensity == "High" and curr.recovery_stage <= 1:
            safety_penalty += 0.3

        r_safety = -min(1.0, safety_penalty)

        # ── Movement Quality penalty ─────────────────────────────────────
        if (
            hasattr(curr, "joint_angles")
            and len(curr.joint_angles) > 0
            and "ideal_angles" in locals()
        ):
            # (In a full implementation, pass the ideal angles through 'info' or parameters.
            # Here, we assume the environment computed them, but if missing, penalty is 0)
            deviation = np.mean(
                np.abs(curr.joint_angles - 0.5)
            )  # Fallback, ideally compared to actual ideal
            r_form = -0.10 * deviation
        else:
            r_form = 0.0

        # ── Composite reward ─────────────────────────────────────────────
        c = self.cfg
        reward = (
            c.w_pain * r_pain
            + c.w_rom * r_rom
            + c.w_strength * r_strength
            + c.w_adherence * r_adherence
            + c.w_safety * r_safety
            + r_form
        )

        components = {
            "pain": round(r_pain, 3),
            "rom": round(r_rom, 3),
            "strength": round(r_strength, 3),
            "adherence": round(r_adherence, 3),
            "safety": round(r_safety, 3),
            "total": round(reward, 3),
        }
        return float(np.clip(reward, -1.0, 1.0)), components


# ─── Patient Dynamics ────────────────────────────────────────────────────────────


class PatientDynamics:
    """
    Stochastic forward model of patient recovery.
    Simulates how a patient's state evolves after a prescription session.
    """

    def __init__(self, cfg: EnvConfig, rng: np.random.Generator):
        self.cfg = cfg
        self.rng = rng

    def _noise(self, scale: float = 1.0) -> float:
        return float(self.rng.normal(0, self.cfg.noise_std * scale))

    def step(
        self,
        state: PatientState,
        action_id: int,
    ) -> Tuple[PatientState, bool]:
        """
        Apply a prescription and return the next state.
        Returns (next_state, overtraining_flag).
        """
        p = get_prescription(action_id)
        nxt = state.clone()
        nxt.session_number += 1
        nxt.days_since = float(self.rng.integers(1, 4))

        # ── Intensity multiplier ─────────────────────────────────────────
        int_mult = {"Low": 0.7, "Moderate": 1.0, "High": 1.4}[p.intensity]
        prog_mult = {"Regress": 0.6, "Maintain": 0.9, "Progress": 1.2}[p.progression]
        load = int_mult * prog_mult

        overtraining = False

        # ── Stage mismatch penalty ───────────────────────────────────────
        stage_gap = abs(p.stage - state.recovery_stage)
        mismatch_penalty = stage_gap * 0.05

        # ── Pain dynamics ────────────────────────────────────────────────
        # Appropriate loading reduces pain; excessive loading increases it
        if load > 1.3 and state.pain_level > 0.5:
            pain_delta = 0.05 * load + self._noise()  # pain worsens
            overtraining = True
        elif p.stage <= state.recovery_stage:
            pain_delta = -0.08 * (1 - state.pain_level) + self._noise()  # pain improves
        else:
            pain_delta = 0.03 * stage_gap + self._noise()  # mismatch → pain
        nxt.pain_level = float(
            np.clip(state.pain_level + pain_delta + mismatch_penalty, 0.0, 1.0)
        )

        # ── ROM dynamics ─────────────────────────────────────────────────
        rom_gain_rate = 0.04 * min(1.0, load * 0.8) * (1 - state.rom)
        if p.stage > state.recovery_stage + 1:
            rom_gain_rate *= 0.3  # inappropriate stage slows progress
        nxt.rom = float(np.clip(state.rom + rom_gain_rate + self._noise(), 0.0, 1.0))

        # ── Strength dynamics ─────────────────────────────────────────────
        if p.intensity in ("Moderate", "High") and p.stage >= state.recovery_stage:
            str_gain = 0.03 * load * (1 - state.strength) + self._noise()
        else:
            str_gain = 0.01 * (1 - state.strength) + self._noise()  # maintenance
        nxt.strength = float(np.clip(state.strength + str_gain, 0.0, 1.0))

        # ── Movement quality ─────────────────────────────────────────────
        mq_gain = 0.025 * (nxt.rom + nxt.strength) / 2.0 + self._noise(0.5)
        nxt.movement_quality = float(
            np.clip(state.movement_quality + mq_gain, 0.0, 1.0)
        )

        # ── Fatigue dynamics ──────────────────────────────────────────────
        fatigue_increase = 0.1 * load
        if overtraining:
            fatigue_increase *= 2.0
        recovery = 0.15 * (nxt.days_since / 3.0)
        nxt.fatigue = float(
            np.clip(
                state.fatigue + fatigue_increase - recovery + self._noise(0.5), 0.0, 1.0
            )
        )

        # ── Adherence dynamics ────────────────────────────────────────────
        # High pain or fatigue reduces adherence; good progress increases it
        pain_effect = -0.05 if nxt.pain_level > 0.6 else 0.02
        progress_effect = 0.03 if (nxt.rom - state.rom) > 0.01 else 0.0
        nxt.adherence = float(
            np.clip(
                state.adherence + pain_effect + progress_effect + self._noise(0.3),
                0.1,
                1.0,
            )
        )

        # ── Recovery stage progression ────────────────────────────────────
        stage_threshold = [0.5, 0.62, 0.74, 0.85]  # composite score to advance
        composite = (nxt.rom + nxt.strength) / 2.0
        if (
            state.recovery_stage < 4
            and composite >= stage_threshold[state.recovery_stage]
        ):
            nxt.recovery_stage = state.recovery_stage + 1

        return nxt, overtraining


# ─── Environment ────────────────────────────────────────────────────────────────


class RehabEnvironment:
    """
    OpenAI-Gym-style rehabilitation environment.

    Usage:
        env = RehabEnvironment()
        state_vec = env.reset()
        while not done:
            action = agent.act(state_vec)
            next_vec, reward, done, info = env.step(action)

    Optional mHealth integration:
        env = RehabEnvironment(use_mhealth=True, mhealth_data_dir="datasets/mhealth")
    """

    def __init__(
        self,
        cfg: Optional[EnvConfig] = None,
        seed: int = 42,
        use_mhealth: bool = False,
        mhealth_data_dir: Optional[str] = None,
        movena_data_dir: Optional[str] = None,
    ):
        self.cfg = cfg or EnvConfig()
        self.rng = np.random.default_rng(seed)
        self.dynamics = PatientDynamics(self.cfg, self.rng)
        self.reward_fn = RewardFunction(self.cfg)

        self.state_dim = STATE_DIM
        self.n_actions = N_ACTIONS

        # mHealth data integration
        self.use_mhealth = use_mhealth and MHEALTH_AVAILABLE
        self.mhealth_loader = None
        self.mhealth_windows = []
        self.current_mhealth_idx = 0

        self.rehab24_loader = (
            Rehab246Loader(movena_data_dir) if movena_data_dir else None
        )
        self.current_rehab24_profile: Optional[Rehab246Profile] = None

        if self.use_mhealth:
            if mhealth_data_dir is None:
                mhealth_data_dir = str(MHEALTH_DATA_DIR)
            if os.path.exists(mhealth_data_dir):
                self.mhealth_loader = MHealthLoader(mhealth_data_dir)
                self.mhealth_windows = self.mhealth_loader.create_training_windows()
                print(f"Loaded {len(self.mhealth_windows)} mHealth sensor windows")
            else:
                print(f"Warning: mHealth data directory not found: {mhealth_data_dir}")
                self.use_mhealth = False

        self._state: PatientState = PatientState()
        self._step_count: int = 0
        self._trajectory: List[Dict] = []
        self._current_activity: Optional[int] = (
            None  # Track mHealth activity for episode
        )

    # ── Gym interface ─────────────────────────────────────────────────────
    def reset(
        self,
        injury_type: Optional[str] = None,
        injury_severity: Optional[float] = None,
        recovery_stage: int = 0,
    ) -> np.ndarray:
        """Reset environment with a new (possibly random) patient."""
        inj = injury_type or self.rng.choice(INJURY_TYPES)
        sev = (
            injury_severity
            if injury_severity is not None
            else float(self.rng.uniform(0.4, 0.9))
        )

        # Initialize with mHealth-based metrics if enabled
        if self.use_mhealth and self.mhealth_windows:
            # Get a random mHealth window to influence initial state
            mhealth_window = self.rng.choice(self.mhealth_windows)
            metrics = activity_to_rehab_metrics(mhealth_window.activity)

            # Map activity metrics to patient state
            self._state = PatientState(
                injury_type=inj,
                injury_severity=sev,
                recovery_stage=recovery_stage,
                pain_level=float(self.rng.uniform(0.3, 0.8)),
                rom=float(self.rng.uniform(0.3, 0.7)),
                strength=float(self.rng.uniform(0.3, 0.6)),
                movement_quality=float(metrics.get("rom_benefit", 0.5)),
                fatigue=float(metrics.get("fatigue", 0.3)),
                adherence=float(self.rng.uniform(0.7, 0.95)),
                days_since=float(self.rng.integers(1, 3)),
                session_number=1,
            )
            # Store mHealth activity for this episode
            self._current_activity = mhealth_window.activity
        else:
            self._state = PatientState(
                injury_type=inj,
                injury_severity=sev,
                recovery_stage=recovery_stage,
                pain_level=float(self.rng.uniform(0.3, 0.8)),
                rom=float(self.rng.uniform(0.3, 0.7)),
                strength=float(self.rng.uniform(0.3, 0.6)),
                movement_quality=float(self.rng.uniform(0.3, 0.6)),
                fatigue=float(self.rng.uniform(0.1, 0.4)),
                adherence=float(self.rng.uniform(0.7, 0.95)),
                days_since=float(self.rng.integers(1, 3)),
                session_number=1,
            )
            self._current_activity = None

        # External motion capture enriches only the simulated joint geometry.
        # Source correctness labels deliberately do not affect state or reward.
        if self.rehab24_loader is not None:
            self.current_rehab24_profile = self.rehab24_loader.sample(self.rng)
            self._state.joint_angles = (
                self.current_rehab24_profile.joint_angles.copy()
            )
        else:
            self.current_rehab24_profile = None

        self._step_count = 0
        self._trajectory = []
        return self._state.to_vector()

    def step(self, action: int) -> Tuple[np.ndarray, float, bool, Dict]:
        """Apply action, simulate patient response, return (obs, reward, done, info)."""
        assert 0 <= action < self.n_actions, f"Invalid action {action}"
        prev = self._state.clone()

        next_state, overtraining = self.dynamics.step(self._state, action)
        reward, components = self.reward_fn.compute(
            prev, next_state, action, overtraining
        )

        self._state = next_state
        self._step_count += 1

        # Episode termination
        composite = (next_state.rom + next_state.strength) / 2.0
        recovered = (
            composite >= self.cfg.recovery_threshold and next_state.recovery_stage == 4
        )
        timed_out = self._step_count >= self.cfg.max_sessions
        done = recovered or timed_out

        info = {
            "step": self._step_count,
            "state_summary": next_state.summary(),
            "overtraining": overtraining,
            "reward_components": components,
            "recovered": recovered,
            "composite": round(composite, 3),
            "prescription": get_prescription(action).name,
        }
        self._trajectory.append(
            {
                "session": self._step_count,
                "reward": round(reward, 3),
                **next_state.summary(),
                **{f"r_{k}": v for k, v in components.items()},
            }
        )
        return next_state.to_vector(), reward, done, info

    # ── Helpers ───────────────────────────────────────────────────────────
    def get_state(self) -> PatientState:
        return self._state

    def get_trajectory(self):
        import pandas as pd

        return pd.DataFrame(self._trajectory)

    def valid_actions(self) -> List[int]:
        """Return action IDs appropriate for current recovery stage (±1 stage tolerance)."""
        stage = self._state.recovery_stage
        return [p.action_id for p in ACTION_SPACE if abs(p.stage - stage) <= 1]

    def render(self) -> str:
        s = self._state.summary()
        return (
            f"[Session {self._step_count}] Stage: {s['stage']} | "
            f"Pain: {s['pain']}/10 | ROM: {s['rom_pct']}% | "
            f"Strength: {s['str_pct']}% | Adherence: {s['adherence']}%"
        )


# ─── Real Data Environment ─────────────────────────────────────────────────────


class RealDataEnvironment:
    """
    Rehabilitation environment powered by real mHealth sensor data.

    Instead of stochastic simulation, patient state evolves based on actual
    sensor data from real subjects performing the 12 activities.

    Usage:
        env = RealDataEnvironment(mhealth_data_dir="datasets/mhealth")
        state_vec = env.reset(subject_id=1)
        while not done:
            action = agent.act(state_vec)
            next_vec, reward, done, info = env.step(action)
    """

    def __init__(
        self,
        cfg: Optional[EnvConfig] = None,
        seed: int = 42,
        mhealth_data_dir: Optional[str] = None,
    ):
        if not MHEALTH_AVAILABLE:
            raise RuntimeError(
                "RealDataEnvironment requires mHealth loader. Please check data/mhealth_loader.py"
            )

        self.cfg = cfg or EnvConfig()
        self.rng = np.random.default_rng(seed)
        self.reward_fn = RewardFunction(self.cfg)

        self.state_dim = 32
        self.n_actions = N_ACTIONS

        # Load UIPRMD Data
        try:
            from rehabrl.data.ui_prmd_loader import UIPRMDLoader

            self.prmd_loader = UIPRMDLoader()
        except ImportError:
            self.prmd_loader = None

        # Load mHealth data
        if mhealth_data_dir is None:
            mhealth_data_dir = os.path.join(
                os.path.dirname(__file__), "data", "MHEALTHDATASET"
            )

        self.mhealth_loader = MHealthLoader(mhealth_data_dir)
        self.mhealth_windows = self.mhealth_loader.create_training_windows()
        print(
            f"✓ RealDataEnvironment loaded {len(self.mhealth_windows)} sensor windows from {mhealth_data_dir}"
        )

        self._state: PatientState = PatientState()
        self._step_count: int = 0
        self._trajectory: List[Dict] = []
        self._current_windows: List = []  # Current subject's activity windows
        self._window_idx: int = 0
        self._current_subject: Optional[int] = None
        self._current_activity: Optional[int] = None

    def reset(
        self,
        subject_id: Optional[int] = None,
        injury_type: Optional[str] = None,
        recovery_stage: int = 0,
    ) -> np.ndarray:
        """Reset with a specific mHealth subject's data."""
        if subject_id is None:
            subject_id = self.rng.integers(1, 11)

        # Get windows for this subject
        subject_windows = [
            w for w in self.mhealth_windows if w.subject_id == subject_id
        ]
        if not subject_windows:
            raise ValueError(f"No mHealth data found for subject {subject_id}")

        self._current_subject = subject_id
        self._current_windows = subject_windows
        self._window_idx = 0

        # Initialize patient state from first activity
        first_window = self._current_windows[0]
        metrics = activity_to_rehab_metrics(first_window.activity)
        inj = injury_type or self.rng.choice(INJURY_TYPES)

        # Map activity intensity to pain/ROM/strength
        self._state = PatientState(
            injury_type=inj,
            injury_severity=float(self.rng.uniform(0.4, 0.8)),
            recovery_stage=recovery_stage,
            pain_level=float(np.clip(1.0 - metrics.get("rom_benefit", 0.5), 0.2, 0.8)),
            rom=float(metrics.get("rom_benefit", 0.5)),
            strength=float(metrics.get("strength_benefit", 0.5)),
            movement_quality=float(metrics.get("rom_benefit", 0.5)),
            fatigue=float(metrics.get("fatigue", 0.3)),
            adherence=float(self.rng.uniform(0.75, 0.95)),
            days_since=float(self.rng.integers(1, 3)),
            session_number=1,
        )
        self._current_activity = first_window.activity

        self._step_count = 0
        self._trajectory = []
        return self._state.to_vector()

    def step(self, action: int) -> Tuple[np.ndarray, float, bool, Dict]:
        """
        Apply action and advance through sensor data stream.
        State transitions are guided by real sensor data characteristics.
        """
        assert 0 <= action < self.n_actions

        prev = self._state.clone()

        # Get next activity from sensor stream
        if self._window_idx < len(self._current_windows):
            window = self._current_windows[self._window_idx]
            metrics = activity_to_rehab_metrics(window.activity)
            self._current_activity = window.activity
            self._window_idx += 1
        else:
            # If we've gone through all windows, cycle or reset
            self._window_idx = 0
            window = self._current_windows[0]
            metrics = activity_to_rehab_metrics(window.activity)

        # Update state based on sensor-derived metrics and prescription
        prescription = get_prescription(action)
        nxt = prev.clone()
        nxt.session_number += 1
        nxt.days_since = 1.0

        # Blend prescription guidance with sensor-based activity response
        activity_intensity = metrics.get("intensity", 0.5)

        # Pain dynamics: better adherence to prescription reduces pain
        stage_match = 1.0 - (abs(prescription.stage - prev.recovery_stage) * 0.2)
        pain_improvement = metrics.get("rom_benefit", 0.5) * stage_match * 0.1
        nxt.pain_level = float(
            np.clip(prev.pain_level - pain_improvement + self.rng.normal(0, 0.03), 0, 1)
        )

        # ROM/Strength: based on activity benefits
        rom_gain = metrics.get("rom_benefit", 0.3) * (1 - prev.rom) * 0.08
        nxt.rom = float(np.clip(prev.rom + rom_gain + self.rng.normal(0, 0.02), 0, 1))

        str_gain = metrics.get("strength_benefit", 0.3) * (1 - prev.strength) * 0.06
        nxt.strength = float(
            np.clip(prev.strength + str_gain + self.rng.normal(0, 0.02), 0, 1)
        )

        # Movement quality from sensor data quality
        mq_gain = activity_intensity * 0.05
        nxt.movement_quality = float(np.clip(prev.movement_quality + mq_gain, 0, 1))

        # Fatigue from activity intensity
        nxt.fatigue = float(
            np.clip(prev.fatigue + (activity_intensity * 0.15) - 0.08, 0, 1)
        )

        # Adherence: good progress and pain control improve adherence
        if nxt.pain_level < prev.pain_level or nxt.rom > prev.rom:
            nxt.adherence = min(1.0, prev.adherence + 0.02)
        else:
            nxt.adherence = max(0.1, prev.adherence - 0.01)

        # Stage progression
        composite = (nxt.rom + nxt.strength) / 2.0
        stage_thresholds = [0.5, 0.62, 0.74, 0.85]
        if (
            prev.recovery_stage < 4
            and composite >= stage_thresholds[prev.recovery_stage]
        ):
            nxt.recovery_stage = prev.recovery_stage + 1

        # Calculate Joint angles using real UI-PRMD data
        exercise_name = "squat"  # Default mapping for rehab exercises
        if "lunge" in prescription.name.lower():
            exercise_name = "lunge"
        elif "press" in prescription.name.lower():
            exercise_name = "leg_press"

        if self.prmd_loader:
            try:
                profile = self.prmd_loader.compute_average_angle_profile(exercise_name)
                # Take average across time to represent session angles, take first 6 joints
                base_angles = np.mean(profile, axis=0)[:6]
                nxt.joint_angles = base_angles * (0.8 + 0.2 * nxt.movement_quality)
            except Exception:
                nxt.joint_angles = np.zeros(6)
        else:
            nxt.joint_angles = np.zeros(6)

        self._state = nxt
        self._step_count += 1

        # Compute reward
        reward, components = self.reward_fn.compute(
            prev, nxt, action, overtraining=False
        )

        # Episode termination
        recovered = composite >= self.cfg.recovery_threshold and nxt.recovery_stage == 4
        timed_out = (
            self._step_count >= self.cfg.max_sessions
            or self._window_idx >= len(self._current_windows)
        )
        done = recovered or timed_out

        info = {
            "step": self._step_count,
            "subject_id": self._current_subject,
            "activity": self._current_activity,
            "state_summary": nxt.summary(),
            "reward_components": components,
            "recovered": recovered,
            "composite": round(composite, 3),
            "prescription": prescription.name,
        }

        self._trajectory.append(
            {
                "session": self._step_count,
                "reward": round(reward, 3),
                "subject": self._current_subject,
                "activity": self._current_activity,
                **nxt.summary(),
                **{f"r_{k}": v for k, v in components.items()},
            }
        )

        return nxt.to_vector(), reward, done, info

    def get_subject_info(self, subject_id: int) -> Dict:
        """Get statistics for a specific subject."""
        windows = [w for w in self.mhealth_windows if w.subject_id == subject_id]
        activities = {}
        for w in windows:
            activities[w.activity] = activities.get(w.activity, 0) + 1

        from rehabrl.data.mhealth_loader import ACTIVITY_LABELS

        return {
            "subject_id": subject_id,
            "total_windows": len(windows),
            "activities": {
                ACTIVITY_LABELS.get(act, f"Activity {act}"): count
                for act, count in activities.items()
            },
        }

    def get_all_subjects(self) -> List[int]:
        """Return list of available subject IDs."""
        return sorted(list(set(w.subject_id for w in self.mhealth_windows)))

    def get_trajectory(self):
        import pandas as pd

        return pd.DataFrame(self._trajectory)

    def get_state(self) -> PatientState:
        return self._state

    def valid_actions(self) -> List[int]:
        """Return action IDs appropriate for current recovery stage."""
        stage = self._state.recovery_stage
        return [p.action_id for p in ACTION_SPACE if abs(p.stage - stage) <= 1]
