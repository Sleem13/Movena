"""Flexed -> extended -> flexed knee-extension repetition state machine."""

from __future__ import annotations

from statistics import mean, pstdev

from app.services.signal_processing_service import compute_angle_stability, smooth_squat_angles

from .schemas import KneeExtensionCountResult, KneeExtensionRepEvent
from .thresholds import (
    EXTENDED_KNEE_ANGLE_MIN, FLEXED_KNEE_ANGLE_MAX, MAX_REP_DURATION_SEC,
    MIN_ANGLE_RANGE, MIN_FRAMES_BETWEEN_REPS, MIN_PHASE_FRAMES, MIN_REP_DURATION_SEC,
)


def _fill(values: list[float | None], fallback: list[float]) -> list[float]:
    first = next((float(value) for value in values if value is not None), fallback[0] if fallback else 0.0)
    result: list[float] = []
    previous = first
    for value in values:
        if value is not None:
            previous = float(value)
        result.append(round(previous, 2))
    return result


def count_knee_extension_reps(
    knee_angles: list[float],
    timestamps: list[float] | None = None,
    frame_indexes: list[int] | None = None,
    low_confidence_mask: list[bool] | None = None,
    pose_quality_score: float = 1.0,
    pose_detection_rate: float = 1.0,
) -> KneeExtensionCountResult:
    if not knee_angles:
        return KneeExtensionCountResult()
    indexes = frame_indexes or list(range(len(knee_angles)))
    processed = smooth_squat_angles(knee_angles, low_confidence_mask)
    angles = _fill(processed, knee_angles)
    phases = ["unreliable"] * len(angles)
    transitions: list[str] = []
    events: list[KneeExtensionRepEvent] = []
    ignored = 0
    state = "seeking_flexed"
    flexed_run = extended_run = 0
    start_pos: int | None = None
    extended_pos: int | None = None
    minimum = 180.0
    maximum = 0.0
    previous: float | None = None
    last_end_frame = -MIN_FRAMES_BETWEEN_REPS
    has_timing = bool(timestamps and len(timestamps) == len(angles) and timestamps[-1] > timestamps[0])

    def transition(new_state: str, position: int) -> None:
        nonlocal state
        transitions.append(f"{state}->{new_state}@{indexes[position]}")
        state = new_state

    def reset_flexed(position: int) -> None:
        nonlocal flexed_run, extended_run, start_pos, extended_pos, minimum, maximum
        transition("flexed", position)
        flexed_run, extended_run = 1, 0
        start_pos = extended_pos = None
        minimum = maximum = angles[position]

    for position, angle in enumerate(angles):
        missing = processed[position] is None
        gap = position > 0 and indexes[position] - indexes[position - 1] > 3
        if missing or gap:
            if state in {"extending", "extended", "returning"}:
                ignored += 1
            state = "seeking_flexed"
            flexed_run = extended_run = 0
            start_pos = extended_pos = None
            previous = None
            continue
        is_flexed = angle <= FLEXED_KNEE_ANGLE_MAX
        is_extended = angle >= EXTENDED_KNEE_ANGLE_MIN
        increasing = previous is not None and angle > previous + 0.5
        decreasing = previous is not None and angle < previous - 0.5

        if state == "seeking_flexed":
            phases[position] = "flexed" if is_flexed else "unknown"
            flexed_run = flexed_run + 1 if is_flexed else 0
            if flexed_run >= MIN_PHASE_FRAMES:
                reset_flexed(position)
        elif state == "flexed":
            phases[position] = "flexed"
            if is_flexed:
                flexed_run += 1
                minimum = min(minimum, angle)
            elif increasing and indexes[position] - last_end_frame >= MIN_FRAMES_BETWEEN_REPS:
                transition("extending", position)
                phases[position] = "extending"
                start_pos = max(0, position - 1)
                minimum = min(minimum, angles[start_pos])
                maximum = max(angle, angles[start_pos])
                extended_run = 0
            else:
                flexed_run = 0
        elif state == "extending":
            phases[position] = "extending"
            minimum, maximum = min(minimum, angle), max(maximum, angle)
            extended_run = extended_run + 1 if is_extended else 0
            if extended_run >= MIN_PHASE_FRAMES:
                extended_pos = position - MIN_PHASE_FRAMES + 1
                transition("extended", position)
                for phase_pos in range(extended_pos, position + 1):
                    phases[phase_pos] = "extended"
            elif is_flexed and not increasing:
                if maximum - minimum >= MIN_ANGLE_RANGE / 2:
                    ignored += 1
                reset_flexed(position)
        elif state == "extended":
            phases[position] = "extended"
            maximum = max(maximum, angle)
            if not is_extended and decreasing:
                transition("returning", position)
                phases[position] = "returning"
                flexed_run = 0
        else:
            phases[position] = "returning"
            minimum = min(minimum, angle)
            flexed_run = flexed_run + 1 if is_flexed else 0
            if flexed_run >= MIN_PHASE_FRAMES:
                start = start_pos if start_pos is not None else 0
                duration = float(timestamps[position] - timestamps[start]) if has_timing and timestamps is not None else None
                angle_range = maximum - minimum
                valid_duration = duration is None or MIN_REP_DURATION_SEC <= duration <= MAX_REP_DURATION_SEC
                if extended_pos is not None and angle_range >= MIN_ANGLE_RANGE and valid_duration:
                    events.append(KneeExtensionRepEvent(
                        start_frame=indexes[start], extended_frame=indexes[extended_pos], end_frame=indexes[position],
                        duration_sec=round(duration, 3) if duration is not None else None,
                        minimum_knee_angle=round(minimum, 2), maximum_knee_angle=round(maximum, 2),
                        angle_range=round(angle_range, 2),
                    ))
                    last_end_frame = indexes[position]
                else:
                    ignored += 1
                reset_flexed(position)
        previous = angle

    if state in {"extending", "extended", "returning"}:
        ignored += 1
    durations = [event.duration_sec for event in events if event.duration_sec is not None]
    if events:
        completion = len(events) / (len(events) + ignored)
        range_clarity = mean(min(1.0, event.angle_range / 50.0) for event in events)
        duration_consistency = max(0.0, 1 - pstdev(durations) / mean(durations)) if len(durations) > 1 and mean(durations) else 0.85
        confidence = (
            0.30 * completion + 0.25 * (0.65 * pose_quality_score + 0.35 * pose_detection_rate)
            + 0.20 * range_clarity + 0.15 * compute_angle_stability(processed) + 0.10 * duration_consistency
        )
    else:
        confidence = 0.0
    return KneeExtensionCountResult(
        total_reps=len(events), valid_reps=len(events), ignored_partial_reps=ignored,
        confidence=round(max(0.0, min(1.0, confidence)), 3), rep_events=events,
        rep_durations=[float(value) for value in durations], phases=phases,
        phase_transitions=transitions, smoothed_knee_angles=angles,
    )

