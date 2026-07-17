"""Internal structures for shoulder-abduction analysis."""

from dataclasses import dataclass, field


@dataclass
class ShoulderAbductionRepEvent:
    start_frame: int
    raised_frame: int
    end_frame: int
    duration_sec: float | None
    minimum_angle: float
    maximum_angle: float
    angle_range: float


@dataclass
class ShoulderAbductionCountResult:
    total_reps: int = 0
    valid_reps: int = 0
    ignored_partial_reps: int = 0
    confidence: float = 0.0
    rep_events: list[ShoulderAbductionRepEvent] = field(default_factory=list)
    rep_durations: list[float] = field(default_factory=list)
    phases: list[str] = field(default_factory=list)
    phase_transitions: list[str] = field(default_factory=list)
    smoothed_angles: list[float] = field(default_factory=list)


@dataclass
class ShoulderAbductionValidity:
    is_valid: bool
    reason: str | None
    angle_range: float
    valid_reps: int
    warnings: list[str] = field(default_factory=list)


@dataclass
class ShoulderAbductionScore:
    total: int
    abduction_range_score: int
    control_score: int
    consistency_score: int
    posture_visibility_score: int
    rep_completion_score: int
    issues: list[str] = field(default_factory=list)
