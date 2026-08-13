"""Internal balance-analysis data structures."""

from dataclasses import dataclass, field


@dataclass
class BalanceScore:
    total: int
    hold_duration_score: int
    sway_control_score: int
    trunk_control_score: int
    pelvis_control_score: int
    knee_stability_score: int
    posture_visibility_score: int
    issues: list[str] = field(default_factory=list)

