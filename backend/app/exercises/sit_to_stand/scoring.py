"""Transparent educational movement scoring for valid sit-to-stand sets."""

from statistics import mean, pstdev

from app.schemas.analysis_schema import PoseQuality

from .schemas import SitToStandCountResult, SitToStandScore
from .thresholds import EXCESSIVE_TRUNK_LEAN_ANGLE, TRUNK_LEAN_WARNING_ANGLE


def score_sit_to_stand(
    count: SitToStandCountResult, trunk_angles: list[float], pose_quality: PoseQuality,
) -> SitToStandScore:
    completion = round(100 * count.total_reps / max(1, count.total_reps + count.ignored_partial_reps))
    durations = count.rep_durations
    consistency = round(max(0, 100 * (1 - pstdev(durations) / mean(durations)))) if len(durations) > 1 and mean(durations) else 85
    control = round(100 * min(1.0, 0.6 * count.confidence + 0.4 * (consistency / 100)))
    excessive_ratio = sum(value >= EXCESSIVE_TRUNK_LEAN_ANGLE for value in trunk_angles) / max(1, len(trunk_angles))
    warning_ratio = sum(value >= TRUNK_LEAN_WARNING_ANGLE for value in trunk_angles) / max(1, len(trunk_angles))
    trunk = round(max(0, 100 - 70 * excessive_ratio - 25 * warning_ratio))
    pose = round(pose_quality.score * 100)
    symmetry = 50  # Explicit placeholder until a validated bilateral metric is designed.
    issues: list[str] = []
    if count.ignored_partial_reps:
        issues.append("incomplete_stand")
    if excessive_ratio > 0.10:
        issues.append("excessive_trunk_lean")
    if durations and any(value < 1.5 for value in durations):
        issues.append("fast_uncontrolled_movement")
    if control < 60:
        issues.append("poor_control")
    if pose_quality.score < 0.60:
        issues.append("low_confidence_tracking")
    total = round(0.30 * completion + 0.25 * control + 0.20 * trunk + 0.15 * consistency + 0.10 * pose)
    return SitToStandScore(total, completion, control, trunk, consistency, pose, symmetry, issues)
