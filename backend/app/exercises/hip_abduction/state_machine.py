"""Neutral -> abducted -> neutral hip-abduction repetition state machine."""

from __future__ import annotations

from statistics import mean, pstdev

from app.services.signal_processing_service import compute_angle_stability, moving_average

from .schemas import HipAbductionCountResult, HipAbductionRepEvent
from .thresholds import ABDUCTED_ANGLE_MIN, MAX_REP_DURATION_SEC, MIN_ANGLE_RANGE, MIN_FRAMES_BETWEEN_REPS, MIN_PHASE_FRAMES, MIN_REP_DURATION_SEC, NEUTRAL_ANGLE_MAX


def count_hip_abduction_reps(angles: list[float], timestamps: list[float] | None = None, frame_indexes: list[int] | None = None, low_confidence_mask: list[bool] | None = None, pose_quality_score: float = 1.0, pose_detection_rate: float = 1.0) -> HipAbductionCountResult:
    if not angles:
        return HipAbductionCountResult()
    indexes = frame_indexes or list(range(len(angles)))
    smoothed = [round(value, 2) for value in moving_average(angles, 3)]
    missing = low_confidence_mask if low_confidence_mask and len(low_confidence_mask) == len(angles) else [False] * len(angles)
    processed = [None if missing[index] else value for index, value in enumerate(smoothed)]
    phases = ["unreliable"] * len(angles)
    transitions: list[str] = []
    events: list[HipAbductionRepEvent] = []
    ignored = 0
    state = "seeking_neutral"
    neutral_run = abducted_run = 0
    start_pos = abducted_pos = None
    minimum, maximum = 180.0, 0.0
    previous = None
    last_end_frame = -MIN_FRAMES_BETWEEN_REPS
    has_timing = bool(timestamps and len(timestamps) == len(angles) and timestamps[-1] > timestamps[0])

    def transition(new_state: str, position: int) -> None:
        nonlocal state
        transitions.append(f"{state}->{new_state}@{indexes[position]}")
        state = new_state

    def reset_neutral(position: int) -> None:
        nonlocal neutral_run, abducted_run, start_pos, abducted_pos, minimum, maximum
        transition("neutral", position)
        neutral_run, abducted_run = 1, 0
        start_pos = abducted_pos = None
        minimum = maximum = smoothed[position]

    for position, angle in enumerate(smoothed):
        if missing[position] or (position and indexes[position] - indexes[position - 1] > 3):
            if state in {"abducting", "abducted", "returning"}:
                ignored += 1
            state, neutral_run, abducted_run, start_pos, abducted_pos, previous = "seeking_neutral", 0, 0, None, None, None
            continue
        neutral, abducted = angle <= NEUTRAL_ANGLE_MAX, angle >= ABDUCTED_ANGLE_MIN
        increasing = previous is not None and angle > previous + .35
        decreasing = previous is not None and angle < previous - .35
        if state == "seeking_neutral":
            phases[position] = "neutral" if neutral else "unknown"
            neutral_run = neutral_run + 1 if neutral else 0
            if neutral_run >= MIN_PHASE_FRAMES:
                reset_neutral(position)
        elif state == "neutral":
            phases[position] = "neutral"
            if neutral:
                neutral_run += 1
                minimum = min(minimum, angle)
            elif increasing and indexes[position] - last_end_frame >= MIN_FRAMES_BETWEEN_REPS:
                transition("abducting", position)
                phases[position] = "abducting"
                start_pos = max(0, position - 1)
                minimum, maximum = min(minimum, smoothed[start_pos]), max(angle, smoothed[start_pos])
        elif state == "abducting":
            phases[position] = "abducting"
            minimum, maximum = min(minimum, angle), max(maximum, angle)
            abducted_run = abducted_run + 1 if abducted else 0
            if abducted_run >= MIN_PHASE_FRAMES:
                abducted_pos = position - MIN_PHASE_FRAMES + 1
                transition("abducted", position)
                for phase_pos in range(abducted_pos, position + 1):
                    phases[phase_pos] = "abducted"
            elif neutral and not increasing:
                if maximum - minimum >= MIN_ANGLE_RANGE / 2:
                    ignored += 1
                reset_neutral(position)
        elif state == "abducted":
            phases[position] = "abducted"
            maximum = max(maximum, angle)
            if not abducted and decreasing:
                transition("returning", position)
                phases[position] = "returning"
                neutral_run = 0
        else:
            phases[position] = "returning"
            minimum = min(minimum, angle)
            neutral_run = neutral_run + 1 if neutral else 0
            if neutral_run >= MIN_PHASE_FRAMES:
                start = start_pos or 0
                duration = float(timestamps[position] - timestamps[start]) if has_timing and timestamps is not None else None
                angle_range = maximum - minimum
                valid_duration = duration is None or MIN_REP_DURATION_SEC <= duration <= MAX_REP_DURATION_SEC
                if abducted_pos is not None and angle_range >= MIN_ANGLE_RANGE and valid_duration:
                    events.append(HipAbductionRepEvent(indexes[start], indexes[abducted_pos], indexes[position], round(duration, 3) if duration is not None else None, round(minimum, 2), round(maximum, 2), round(angle_range, 2)))
                    last_end_frame = indexes[position]
                else:
                    ignored += 1
                reset_neutral(position)
        previous = angle
    if state in {"abducting", "abducted", "returning"}:
        ignored += 1
    durations = [event.duration_sec for event in events if event.duration_sec is not None]
    if events:
        completion = len(events) / (len(events) + ignored)
        range_clarity = mean(min(1.0, event.angle_range / 35) for event in events)
        duration_consistency = max(0.0, 1 - pstdev(durations) / mean(durations)) if len(durations) > 1 and mean(durations) else .85
        confidence = .30 * completion + .25 * (.65 * pose_quality_score + .35 * pose_detection_rate) + .20 * range_clarity + .15 * compute_angle_stability(processed) + .10 * duration_consistency
    else:
        confidence = 0.0
    return HipAbductionCountResult(len(events), len(events), ignored, round(max(0.0, min(1.0, confidence)), 3), events, [float(value) for value in durations], phases, transitions, smoothed)
