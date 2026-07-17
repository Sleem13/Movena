"""Internal structures for knee-extension analysis."""

from dataclasses import dataclass, field


@dataclass
class KneeExtensionRepEvent:
    start_frame: int
    extended_frame: int
    end_frame: int
    duration_sec: float | None
    minimum_knee_angle: float
    maximum_knee_angle: float
    angle_range: float


@dataclass
class KneeExtensionCountResult:
    total_reps: int = 0
    valid_reps: int = 0
    ignored_partial_reps: int = 0
    confidence: float = 0.0
    rep_events: list[KneeExtensionRepEvent] = field(default_factory=list)
    rep_durations: list[float] = field(default_factory=list)
    phases: list[str] = field(default_factory=list)
    phase_transitions: list[str] = field(default_factory=list)
    smoothed_knee_angles: list[float] = field(default_factory=list)


@dataclass
class KneeExtensionValidity:
    is_valid: bool
    reason: str | None
    knee_angle_range: float
    valid_reps: int
    warnings: list[str] = field(default_factory=list)


@dataclass
class KneeExtensionScore:
    total: int
    extension_range_score: int
    control_score: int
    consistency_score: int
    posture_visibility_score: int
    rep_completion_score: int
    issues: list[str] = field(default_factory=list)

