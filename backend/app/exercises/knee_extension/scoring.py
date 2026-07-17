"""Transparent educational scoring for valid knee-extension repetitions."""

from statistics import mean, pstdev

from app.schemas.analysis_schema import PoseQuality

from .schemas import KneeExtensionCountResult, KneeExtensionScore
from .thresholds import FULL_EXTENSION_REFERENCE, TEMPO_FAST_SEC, TEMPO_INCONSISTENCY_RATIO, TRUNK_COMPENSATION_ANGLE


def _clamp(value: float) -> int:
    return round(max(0.0, min(100.0, value)))


def score_knee_extension(
    count: KneeExtensionCountResult, pose_quality: PoseQuality,
    critical_visibility: float, trunk_angles: list[float] | None = None,
) -> KneeExtensionScore:
    events = count.rep_events
    average_maximum = mean(event.maximum_knee_angle for event in events)
    average_range = mean(event.angle_range for event in events)
    extension = _clamp(50 + 50 * (average_maximum - 155) / (FULL_EXTENSION_REFERENCE - 155))
    completion = _clamp(100 * count.valid_reps / max(1, count.valid_reps + count.ignored_partial_reps))
    durations = count.rep_durations
    consistency = _clamp(100 * (1 - pstdev(durations) / mean(durations))) if len(durations) > 1 and mean(durations) else 85
    control = _clamp(100 * (0.65 * count.confidence + 0.35 * consistency / 100))
    visibility = _clamp(60 * critical_visibility + 40 * pose_quality.pose_detection_rate)
    issues: list[str] = []
    if average_maximum < 165:
        issues.append("limited_knee_extension")
    if average_range < 40:
        issues.append("insufficient_range_of_motion")
    if critical_visibility < 0.65:
        issues.append("poor_visibility")
    if count.ignored_partial_reps:
        issues.append("incomplete_repetition")
    if durations and (any(value < TEMPO_FAST_SEC for value in durations) or (len(durations) > 1 and pstdev(durations) / mean(durations) > TEMPO_INCONSISTENCY_RATIO)):
        issues.append("inconsistent_tempo")
    if trunk_angles and sum(angle >= TRUNK_COMPENSATION_ANGLE for angle in trunk_angles) / len(trunk_angles) > 0.15:
        issues.append("possible_compensation")
    total = _clamp(0.30 * extension + 0.20 * control + 0.20 * consistency + 0.15 * visibility + 0.15 * completion)
    return KneeExtensionScore(total, extension, control, consistency, visibility, completion, issues)

