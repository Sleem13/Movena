"""
rehab_rl/config.py
Central configuration for the Rehabilitation RL system.
"""

from dataclasses import dataclass, field
from pathlib import Path
from typing import List


PROJECT_ROOT = Path(__file__).resolve().parent.parent
CHECKPOINTS_DIR = PROJECT_ROOT / "checkpoints"
DATASETS_DIR = PROJECT_ROOT / "datasets"
EXERCISE_REFERENCE_DIR = DATASETS_DIR / "exercise_reference"
MHEALTH_DATA_DIR = DATASETS_DIR / "mhealth"
SYNTHETIC_DATA_DIR = DATASETS_DIR / "synthetic"


INJURY_TYPES = [
    "ACL Tear",
    "Rotator Cuff Tear",
    "Lumbar Disc Herniation",
    "Ankle Sprain",
    "Tennis Elbow",
    "Patellofemoral Syndrome",
    "Hip Labral Tear",
    "Achilles Tendinopathy",
    "Shoulder Impingement",
    "Plantar Fasciitis",
    "Cervical Strain",
    "Hamstring Strain",
]

RECOVERY_STAGES = [
    "Acute",  # 0-2 weeks
    "Subacute",  # 2-6 weeks
    "Remodeling",  # 6-12 weeks
    "Functional",  # 3-6 months
    "Return",  # 6+ months
]

# State vector layout:
# [injury_type x12 | recovery_stage x5 | pain | rom | strength |
#  movement_quality | fatigue | adherence | days_since | session_norm | severity | joint_angles x6] = 32 dims
STATE_DIM = 32  # = 12 + 5 + 9 continuous metrics + 6 joint angles
N_ACTIONS = 30  # 6 prescriptions × 5 recovery stages


@dataclass
class ModelConfig:
    """Neural network architecture hyperparameters."""

    state_dim: int = STATE_DIM
    n_actions: int = N_ACTIONS
    hidden_dims: List[int] = field(default_factory=lambda: [256, 256, 128])
    dropout: float = 0.15
    use_dueling: bool = True  # Dueling DQN architecture
    use_noisy: bool = False  # Noisy nets (optional)


@dataclass
class TrainingConfig:
    """RL training hyperparameters."""

    # Optimisation
    lr: float = 3e-4
    gamma: float = 0.96  # Discount — high, as recovery is long-horizon
    batch_size: int = 128
    grad_clip: float = 1.0

    # Experience replay
    buffer_size: int = 20_000
    min_buffer: int = 512  # Minimum transitions before training starts
    per_alpha: float = 0.6  # PER: prioritisation exponent
    per_beta_start: float = 0.4  # PER: IS correction start
    per_beta_end: float = 1.0

    # Target network
    target_update: int = 200  # Hard update every N steps
    tau: float = 0.005  # Soft-update coefficient

    # Exploration (ε-greedy)
    eps_start: float = 1.0
    eps_end: float = 0.05
    eps_decay: float = 0.993

    # Loop
    n_episodes: int = 500
    max_steps: int = 50  # Max steps per episode (rehab sessions)
    eval_every: int = 25  # Evaluate every N episodes


@dataclass
class EnvConfig:
    """Patient environment dynamics."""

    # Reward weights (must sum to 1.0)
    w_pain: float = 0.30
    w_rom: float = 0.20
    w_strength: float = 0.20
    w_adherence: float = 0.15
    w_safety: float = 0.15

    # Dynamics noise (simulating inter-patient variability)
    noise_std: float = 0.04

    # Episode termination
    max_sessions: int = 50
    recovery_threshold: float = 0.85  # ROM + Strength combined to "graduate"


@dataclass
class Config:
    model: ModelConfig = field(default_factory=ModelConfig)
    training: TrainingConfig = field(default_factory=TrainingConfig)
    env: EnvConfig = field(default_factory=EnvConfig)
    seed: int = 42
    device: str = "auto"
    save_dir: str = str(CHECKPOINTS_DIR)


# Singleton for convenience
DEFAULT_CONFIG = Config()
