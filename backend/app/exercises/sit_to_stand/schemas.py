"""Internal data structures for sit-to-stand counting and scoring."""

from dataclasses import dataclass, field


@dataclass
class SitToStandRepEvent:
    start_frame: int
    standing_frame: int
    end_frame: int
    duration_sec: float | None
    minimum_knee_angle: float
    maximum_knee_angle: float


@dataclass
class SitToStandCountResult:
    total_reps: int = 0
    rep_events: list[SitToStandRepEvent] = field(default_factory=list)
    rep_durations: list[float] = field(default_factory=list)
    ignored_partial_reps: int = 0
    confidence: float = 0.0
    phases: list[str] = field(default_factory=list)
    smoothed_knee_angles: list[float] = field(default_factory=list)
    smoothed_hip_angles: list[float] = field(default_factory=list)
    transition_clarity: float = 0.0


@dataclass
class SitToStandValidity:
    is_valid: bool
    reason: str | None
    knee_angle_range: float
    hip_angle_range: float
    valid_reps: int
    warnings: list[str] = field(default_factory=list)


@dataclass
class SitToStandScore:
    total: int
    completion_score: int
    control_score: int
    trunk_control_score: int
    consistency_score: int
    pose_confidence_score: int
    symmetry_placeholder_score: int
    issues: list[str] = field(default_factory=list)
