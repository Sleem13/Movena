"""Noise-tolerant sitting -> standing -> sitting repetition state machine."""

from __future__ import annotations

from statistics import mean, pstdev

from app.services.signal_processing_service import compute_angle_stability, smooth_squat_angles

from .schemas import SitToStandCountResult, SitToStandRepEvent
from .thresholds import (
    MAX_REP_DURATION_SEC,
    MIN_ANGLE_DELTA,
    MIN_FRAMES_BETWEEN_REPS,
    MIN_PHASE_FRAMES,
    MIN_REP_DURATION_SEC,
    SITTING_HIP_ANGLE_MAX,
    SITTING_KNEE_ANGLE_MAX,
    STANDING_HIP_ANGLE_MIN,
    STANDING_KNEE_ANGLE_MIN,
)


def _numeric(values: list[float | None], fallback: list[float]) -> list[float]:
    first = next((float(value) for value in values if value is not None), fallback[0] if fallback else 0.0)
    result: list[float] = []
    last = first
    for index, value in enumerate(values):
        if value is not None:
            last = float(value)
        elif index < len(fallback) and 20 <= float(fallback[index]) <= 180:
            last = float(fallback[index])
        result.append(round(last, 2))
    return result


def count_sit_to_stand_reps(
    knee_angles: list[float],
    hip_angles: list[float],
    timestamps: list[float] | None = None,
    frame_indexes: list[int] | None = None,
    low_confidence_mask: list[bool] | None = None,
    pose_quality_score: float = 1.0,
    pose_detection_rate: float = 1.0,
) -> SitToStandCountResult:
    if not knee_angles or len(knee_angles) != len(hip_angles):
        return SitToStandCountResult()
    indexes = frame_indexes or list(range(len(knee_angles)))
    knee_processed = smooth_squat_angles(knee_angles, low_confidence_mask)
    hip_processed = smooth_squat_angles(hip_angles, low_confidence_mask)
    knees = _numeric(knee_processed, knee_angles)
    hips = _numeric(hip_processed, hip_angles)
    phases = ["unreliable"] * len(knees)
    events: list[SitToStandRepEvent] = []
    ignored_partials = 0
    clarity: list[float] = []
    has_timing = bool(timestamps and len(timestamps) == len(knees) and timestamps[-1] > timestamps[0])

    state = "seeking_sitting"
    sit_run = stand_run = 0
    start_pos: int | None = None
    standing_pos: int | None = None
    minimum_knee = minimum_hip = 180.0
    maximum_knee = maximum_hip = 0.0
    last_rep_end = -MIN_FRAMES_BETWEEN_REPS
    previous_knee: float | None = None
    previous_hip: float | None = None

    def sitting(knee: float, hip: float) -> bool:
        return knee <= SITTING_KNEE_ANGLE_MAX and hip <= SITTING_HIP_ANGLE_MAX

    def standing(knee: float, hip: float) -> bool:
        return knee >= STANDING_KNEE_ANGLE_MIN and hip >= STANDING_HIP_ANGLE_MIN

    def reset_to_sitting(position: int) -> None:
        nonlocal state, sit_run, stand_run, start_pos, standing_pos
        nonlocal minimum_knee, minimum_hip, maximum_knee, maximum_hip
        state = "sitting"
        sit_run = 1
        stand_run = 0
        start_pos = standing_pos = None
        minimum_knee = knees[position]
        minimum_hip = hips[position]
        maximum_knee = knees[position]
        maximum_hip = hips[position]

    for position, (knee, hip) in enumerate(zip(knees, hips)):
        raw_missing = knee_processed[position] is None or hip_processed[position] is None
        continuity_break = position > 0 and indexes[position] - indexes[position - 1] > 3
        if raw_missing or continuity_break:
            phases[position] = "unreliable"
            if state in {"rising", "standing", "lowering"}:
                ignored_partials += 1
            state = "seeking_sitting"
            sit_run = stand_run = 0
            start_pos = standing_pos = None
            previous_knee = previous_hip = None
            continue

        is_sitting = sitting(knee, hip)
        is_standing = standing(knee, hip)
        rising_direction = previous_knee is not None and previous_hip is not None and (
            knee > previous_knee + 0.5 or hip > previous_hip + 0.5
        )
        lowering_direction = previous_knee is not None and previous_hip is not None and (
            knee < previous_knee - 0.5 or hip < previous_hip - 0.5
        )

        if state == "seeking_sitting":
            phases[position] = "sitting" if is_sitting else "unknown"
            sit_run = sit_run + 1 if is_sitting else 0
            if sit_run >= MIN_PHASE_FRAMES:
                reset_to_sitting(position)

        elif state == "sitting":
            phases[position] = "sitting"
            if is_sitting:
                sit_run += 1
                minimum_knee = min(minimum_knee, knee)
                minimum_hip = min(minimum_hip, hip)
            elif (
                sit_run >= MIN_PHASE_FRAMES
                and rising_direction
                and indexes[position] - last_rep_end >= MIN_FRAMES_BETWEEN_REPS
            ):
                state = "rising"
                phases[position] = "rising"
                start_pos = max(0, position - 1)
                minimum_knee = min(minimum_knee, knees[start_pos], knee)
                minimum_hip = min(minimum_hip, hips[start_pos], hip)
                maximum_knee = max(knees[start_pos], knee)
                maximum_hip = max(hips[start_pos], hip)
                stand_run = 0
            else:
                sit_run = 0

        elif state == "rising":
            phases[position] = "rising"
            minimum_knee = min(minimum_knee, knee)
            minimum_hip = min(minimum_hip, hip)
            maximum_knee = max(maximum_knee, knee)
            maximum_hip = max(maximum_hip, hip)
            stand_run = stand_run + 1 if is_standing else 0
            if stand_run >= MIN_PHASE_FRAMES:
                state = "standing"
                standing_pos = position - MIN_PHASE_FRAMES + 1
                for phase_pos in range(standing_pos, position + 1):
                    phases[phase_pos] = "standing"
            elif is_sitting and not rising_direction:
                if max(maximum_knee - minimum_knee, maximum_hip - minimum_hip) >= MIN_ANGLE_DELTA / 2:
                    ignored_partials += 1
                reset_to_sitting(position)

        elif state == "standing":
            phases[position] = "standing"
            maximum_knee = max(maximum_knee, knee)
            maximum_hip = max(maximum_hip, hip)
            if not is_standing and lowering_direction:
                state = "lowering"
                phases[position] = "lowering"
                sit_run = 0

        else:  # lowering
            phases[position] = "lowering"
            sit_run = sit_run + 1 if is_sitting else 0
            if sit_run >= MIN_PHASE_FRAMES:
                end_pos = position
                start = start_pos if start_pos is not None else 0
                duration = (
                    float(timestamps[end_pos] - timestamps[start])
                    if has_timing and timestamps is not None else None
                )
                angle_delta = min(maximum_knee - minimum_knee, maximum_hip - minimum_hip)
                duration_valid = duration is None or MIN_REP_DURATION_SEC <= duration <= MAX_REP_DURATION_SEC
                if standing_pos is not None and angle_delta >= MIN_ANGLE_DELTA and duration_valid:
                    events.append(SitToStandRepEvent(
                        start_frame=indexes[start], standing_frame=indexes[standing_pos],
                        end_frame=indexes[end_pos],
                        duration_sec=round(duration, 3) if duration is not None else None,
                        minimum_knee_angle=round(minimum_knee, 2),
                        maximum_knee_angle=round(maximum_knee, 2),
                    ))
                    clarity.append(min(1.0, angle_delta / (MIN_ANGLE_DELTA * 1.5)))
                    last_rep_end = indexes[end_pos]
                else:
                    ignored_partials += 1
                reset_to_sitting(position)

        previous_knee, previous_hip = knee, hip

    if state in {"rising", "standing", "lowering"}:
        ignored_partials += 1
    durations = [event.duration_sec for event in events if event.duration_sec is not None]
    stability = (compute_angle_stability(knee_processed) + compute_angle_stability(hip_processed)) / 2
    transition_clarity = mean(clarity) if clarity else 0.0
    if not events:
        confidence = 0.0
    else:
        completion_ratio = len(events) / (len(events) + ignored_partials)
        duration_consistency = (
            max(0.0, 1 - pstdev(durations) / mean(durations)) if len(durations) > 1 and mean(durations) else 0.85
        )
        pose_factor = 0.7 * pose_quality_score + 0.3 * pose_detection_rate
        confidence = (
            0.30 * completion_ratio + 0.25 * pose_factor + 0.20 * stability
            + 0.15 * transition_clarity + 0.10 * duration_consistency
        )
    return SitToStandCountResult(
        total_reps=len(events), rep_events=events,
        rep_durations=[float(value) for value in durations],
        ignored_partial_reps=ignored_partials,
        confidence=round(max(0.0, min(1.0, confidence)), 3), phases=phases,
        smoothed_knee_angles=knees, smoothed_hip_angles=hips,
        transition_clarity=round(transition_clarity, 3),
    )
