"""Transparent educational scoring for valid shoulder-abduction repetitions."""

from statistics import mean, pstdev

from app.schemas.analysis_schema import PoseQuality

from .schemas import ShoulderAbductionCountResult, ShoulderAbductionScore
from .thresholds import TARGET_ANGLE_MIN, TARGET_ANGLE_MAX, TEMPO_FAST_SEC, TEMPO_INCONSISTENCY_RATIO, TRUNK_COMPENSATION_ANGLE


def _clamp(value: float) -> int:
    return round(max(0.0, min(100.0, value)))


def score_shoulder_abduction(count: ShoulderAbductionCountResult, pose_quality: PoseQuality, critical_visibility: float, trunk_angles: list[float] | None = None, shoulder_hike_rate: float = 0.0) -> ShoulderAbductionScore:
    events = count.rep_events
    average_maximum = mean(event.maximum_angle for event in events)
    average_range = mean(event.angle_range for event in events)
    range_score = _clamp(55 + 45 * (average_maximum - TARGET_ANGLE_MIN) / max(1, TARGET_ANGLE_MAX - TARGET_ANGLE_MIN))
    completion = _clamp(100 * count.valid_reps / max(1, count.valid_reps + count.ignored_partial_reps))
    durations = count.rep_durations
    consistency = _clamp(100 * (1 - pstdev(durations) / mean(durations))) if len(durations) > 1 and mean(durations) else 85
    control = _clamp(100 * (.65 * count.confidence + .35 * consistency / 100))
    visibility = _clamp(60 * critical_visibility + 40 * pose_quality.pose_detection_rate)
    issues = []
    if average_maximum < TARGET_ANGLE_MIN:
        issues.append("limited_observed_abduction_range")
    if average_range < 60:
        issues.append("insufficient_range_of_motion")
    if critical_visibility < .65:
        issues.append("poor_visibility")
    if count.ignored_partial_reps:
        issues.append("incomplete_repetition")
    if durations and (any(value < TEMPO_FAST_SEC for value in durations) or (len(durations) > 1 and pstdev(durations) / mean(durations) > TEMPO_INCONSISTENCY_RATIO)):
        issues.append("inconsistent_tempo")
    if trunk_angles and sum(angle >= TRUNK_COMPENSATION_ANGLE for angle in trunk_angles) / len(trunk_angles) > .15:
        issues.append("possible_trunk_compensation")
    if shoulder_hike_rate > .20:
        issues.append("possible_shoulder_hiking_pattern")
    total = _clamp(.30 * range_score + .20 * control + .20 * consistency + .15 * visibility + .15 * completion)
    return ShoulderAbductionScore(total, range_score, control, consistency, visibility, completion, issues)
