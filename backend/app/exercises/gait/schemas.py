"""Internal structures and public gait metrics."""

from dataclasses import dataclass, field


@dataclass
class GaitCycleEvent:
    side: str
    start_frame: int
    toe_off_frame: int
    end_frame: int
    duration_sec: float
    stance_percent: float
    swing_percent: float
    stride_excursion: float
    knee_range: float


@dataclass
class GaitCountResult:
    total_steps: int = 0
    valid_cycles: int = 0
    confidence: float = 0.0
    cycle_events: list[GaitCycleEvent] = field(default_factory=list)
    cycle_durations: list[float] = field(default_factory=list)
    phases: list[str] = field(default_factory=list)
    phase_transitions: list[str] = field(default_factory=list)
    smoothed_knee_angles: list[float] = field(default_factory=list)


@dataclass
class GaitScore:
    total: int
    gait_phase_score: int
    cadence_score: int
    symmetry_score: int
    stride_consistency_score: int
    kinematic_range_score: int
    posture_visibility_score: int
    issues: list[str] = field(default_factory=list)


