"""Transparent educational scoring for valid shoulder-flexion repetitions."""

from statistics import mean, pstdev

from app.schemas.analysis_schema import PoseQuality

from .schemas import ShoulderFlexionCountResult, ShoulderFlexionScore
from .thresholds import MIN_ELBOW_EXTENSION_ANGLE, TARGET_ANGLE_MAX, TARGET_ANGLE_MIN, TEMPO_FAST_SEC, TEMPO_INCONSISTENCY_RATIO, TRUNK_COMPENSATION_ANGLE


def _clamp(value: float) -> int:
    return round(max(0.0, min(100.0, value)))


def score_shoulder_flexion(count: ShoulderFlexionCountResult, pose_quality: PoseQuality, critical_visibility: float, trunk_angles: list[float] | None = None, shoulder_hike_rate: float = 0.0, elbow_angles: list[float] | None = None) -> ShoulderFlexionScore:
    events = count.rep_events
    average_maximum = mean(event.maximum_angle for event in events)
    average_range = mean(event.angle_range for event in events)
    range_score = _clamp(55 + 45 * (average_maximum - TARGET_ANGLE_MIN) / max(1, TARGET_ANGLE_MAX - TARGET_ANGLE_MIN))
    completion = _clamp(100 * count.valid_reps / max(1, count.valid_reps + count.ignored_partial_reps))
    durations = count.rep_durations
    consistency = _clamp(100 * (1 - pstdev(durations) / mean(durations))) if len(durations) > 1 and mean(durations) else 85
    control = _clamp(100 * (0.65 * count.confidence + 0.35 * consistency / 100))
    visibility = _clamp(60 * critical_visibility + 40 * pose_quality.pose_detection_rate)
    issues = []
    if average_maximum < TARGET_ANGLE_MIN:
        issues.append("limited_observed_flexion_range")
    if average_range < 70:
        issues.append("insufficient_range_of_motion")
    if critical_visibility < 0.65:
        issues.append("poor_visibility")
    if count.ignored_partial_reps:
        issues.append("incomplete_repetition")
    if durations and (any(value < TEMPO_FAST_SEC for value in durations) or (len(durations) > 1 and pstdev(durations) / mean(durations) > TEMPO_INCONSISTENCY_RATIO)):
        issues.append("inconsistent_tempo")
    if trunk_angles and sum(angle >= TRUNK_COMPENSATION_ANGLE for angle in trunk_angles) / len(trunk_angles) > 0.15:
        issues.append("possible_trunk_compensation")
    if shoulder_hike_rate > 0.20:
        issues.append("possible_shoulder_hiking_pattern")
    if elbow_angles and sum(angle < MIN_ELBOW_EXTENSION_ANGLE for angle in elbow_angles) / len(elbow_angles) > 0.25:
        issues.append("possible_elbow_bend_pattern")
    total = _clamp(0.30 * range_score + 0.20 * control + 0.20 * consistency + 0.15 * visibility + 0.15 * completion)
    return ShoulderFlexionScore(total, range_score, control, consistency, visibility, completion, issues)
