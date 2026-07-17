"""Internal structures for hip-abduction analysis."""

from dataclasses import dataclass, field


@dataclass
class HipAbductionRepEvent:
    start_frame: int
    abducted_frame: int
    end_frame: int
    duration_sec: float | None
    minimum_angle: float
    maximum_angle: float
    angle_range: float


@dataclass
class HipAbductionCountResult:
    total_reps: int = 0
    valid_reps: int = 0
    ignored_partial_reps: int = 0
    confidence: float = 0.0
    rep_events: list[HipAbductionRepEvent] = field(default_factory=list)
    rep_durations: list[float] = field(default_factory=list)
    phases: list[str] = field(default_factory=list)
    phase_transitions: list[str] = field(default_factory=list)
    smoothed_angles: list[float] = field(default_factory=list)


@dataclass
class HipAbductionValidity:
    is_valid: bool
    reason: str | None
    angle_range: float
    valid_reps: int
    warnings: list[str] = field(default_factory=list)


@dataclass
class HipAbductionScore:
    total: int
    abduction_range_score: int
    control_score: int
    consistency_score: int
    posture_visibility_score: int
    rep_completion_score: int
    pelvis_trunk_stability_score: int
    issues: list[str] = field(default_factory=list)
