"""Lowered -> raised -> lowered shoulder-abduction repetition state machine."""

from __future__ import annotations

from statistics import mean, pstdev

from app.services.signal_processing_service import compute_angle_stability, smooth_squat_angles

from .schemas import ShoulderAbductionCountResult, ShoulderAbductionRepEvent
from .thresholds import LOWERED_ANGLE_MAX, MAX_REP_DURATION_SEC, MIN_ANGLE_RANGE, MIN_FRAMES_BETWEEN_REPS, MIN_PHASE_FRAMES, MIN_REP_DURATION_SEC, RAISED_ANGLE_MIN


def _fill(values: list[float | None], fallback: list[float]) -> list[float]:
    previous = next((float(value) for value in values if value is not None), fallback[0] if fallback else 0.0)
    result = []
    for value in values:
        if value is not None:
            previous = float(value)
        result.append(round(previous, 2))
    return result


def count_shoulder_abduction_reps(angles: list[float], timestamps: list[float] | None = None, frame_indexes: list[int] | None = None, low_confidence_mask: list[bool] | None = None, pose_quality_score: float = 1.0, pose_detection_rate: float = 1.0) -> ShoulderAbductionCountResult:
    if not angles:
        return ShoulderAbductionCountResult()
    indexes = frame_indexes or list(range(len(angles)))
    processed = smooth_squat_angles(angles, low_confidence_mask)
    smoothed = _fill(processed, angles)
    phases = ["unreliable"] * len(smoothed)
    transitions: list[str] = []
    events: list[ShoulderAbductionRepEvent] = []
    ignored = 0
    state = "seeking_lowered"
    lowered_run = raised_run = 0
    start_pos = raised_pos = None
    minimum, maximum = 180.0, 0.0
    previous = None
    last_end_frame = -MIN_FRAMES_BETWEEN_REPS
    has_timing = bool(timestamps and len(timestamps) == len(smoothed) and timestamps[-1] > timestamps[0])

    def transition(new_state: str, position: int) -> None:
        nonlocal state
        transitions.append(f"{state}->{new_state}@{indexes[position]}")
        state = new_state

    def reset_lowered(position: int) -> None:
        nonlocal lowered_run, raised_run, start_pos, raised_pos, minimum, maximum
        transition("lowered", position)
        lowered_run, raised_run = 1, 0
        start_pos = raised_pos = None
        minimum = maximum = smoothed[position]

    for position, angle in enumerate(smoothed):
        if processed[position] is None or (position and indexes[position] - indexes[position - 1] > 3):
            if state in {"raising", "raised", "lowering"}:
                ignored += 1
            state, lowered_run, raised_run, start_pos, raised_pos, previous = "seeking_lowered", 0, 0, None, None, None
            continue
        lowered, raised = angle <= LOWERED_ANGLE_MAX, angle >= RAISED_ANGLE_MIN
        increasing = previous is not None and angle > previous + .5
        decreasing = previous is not None and angle < previous - .5
        if state == "seeking_lowered":
            phases[position] = "lowered" if lowered else "unknown"
            lowered_run = lowered_run + 1 if lowered else 0
            if lowered_run >= MIN_PHASE_FRAMES:
                reset_lowered(position)
        elif state == "lowered":
            phases[position] = "lowered"
            if lowered:
                lowered_run += 1
                minimum = min(minimum, angle)
            elif increasing and indexes[position] - last_end_frame >= MIN_FRAMES_BETWEEN_REPS:
                transition("raising", position)
                phases[position] = "raising"
                start_pos = max(0, position - 1)
                minimum, maximum = min(minimum, smoothed[start_pos]), max(angle, smoothed[start_pos])
        elif state == "raising":
            phases[position] = "raising"
            minimum, maximum = min(minimum, angle), max(maximum, angle)
            raised_run = raised_run + 1 if raised else 0
            if raised_run >= MIN_PHASE_FRAMES:
                raised_pos = position - MIN_PHASE_FRAMES + 1
                transition("raised", position)
                for phase_pos in range(raised_pos, position + 1):
                    phases[phase_pos] = "raised"
            elif lowered and not increasing:
                if maximum - minimum >= MIN_ANGLE_RANGE / 2:
                    ignored += 1
                reset_lowered(position)
        elif state == "raised":
            phases[position] = "raised"
            maximum = max(maximum, angle)
            if not raised and decreasing:
                transition("lowering", position)
                phases[position] = "lowering"
                lowered_run = 0
        else:
            phases[position] = "lowering"
            minimum = min(minimum, angle)
            lowered_run = lowered_run + 1 if lowered else 0
            if lowered_run >= MIN_PHASE_FRAMES:
                start = start_pos or 0
                duration = float(timestamps[position] - timestamps[start]) if has_timing and timestamps is not None else None
                angle_range = maximum - minimum
                valid_duration = duration is None or MIN_REP_DURATION_SEC <= duration <= MAX_REP_DURATION_SEC
                if raised_pos is not None and angle_range >= MIN_ANGLE_RANGE and valid_duration:
                    events.append(ShoulderAbductionRepEvent(indexes[start], indexes[raised_pos], indexes[position], round(duration, 3) if duration is not None else None, round(minimum, 2), round(maximum, 2), round(angle_range, 2)))
                    last_end_frame = indexes[position]
                else:
                    ignored += 1
                reset_lowered(position)
        previous = angle
    if state in {"raising", "raised", "lowering"}:
        ignored += 1
    durations = [event.duration_sec for event in events if event.duration_sec is not None]
    if events:
        completion = len(events) / (len(events) + ignored)
        range_clarity = mean(min(1.0, event.angle_range / 70) for event in events)
        duration_consistency = max(0.0, 1 - pstdev(durations) / mean(durations)) if len(durations) > 1 and mean(durations) else .85
        confidence = .30 * completion + .25 * (.65 * pose_quality_score + .35 * pose_detection_rate) + .20 * range_clarity + .15 * compute_angle_stability(processed) + .10 * duration_consistency
    else:
        confidence = 0.0
    return ShoulderAbductionCountResult(len(events), len(events), ignored, round(max(0.0, min(1.0, confidence)), 3), events, [float(value) for value in durations], phases, transitions, smoothed)
