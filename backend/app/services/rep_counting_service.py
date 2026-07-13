"""Noise-tolerant squat repetition state machine."""

from __future__ import annotations

from dataclasses import dataclass, field
from statistics import mean, pstdev

from app.core.exercise_thresholds import (
    ANGLE_DIRECTION_EPSILON_DEG,
    ANGLE_SMOOTHING_WINDOW,
    ASCENT_HYSTERESIS_DEG,
    BOTTOM_HOLD_MIN_FRAMES,
    MAX_INTERPOLATED_GAP_FRAMES,
    MAX_AGGREGATED_PARTIAL_EVENTS,
    MAX_REP_DURATION_SEC,
    MIN_DEPTH_DELTA_DEG,
    MIN_FRAMES_BETWEEN_REPS,
    MIN_PARTIAL_MOVEMENT_DELTA_DEG,
    MIN_PHASE_FRAMES,
    MIN_REP_DURATION_SEC,
    PARTIAL_EVENT_MERGE_GAP_FRAMES,
    SQUAT_ATTEMPT_KNEE_ANGLE_DEG,
    STANDING_KNEE_ANGLE_DEG,
)
from app.services.signal_processing_service import compute_angle_stability, smooth_squat_angles


@dataclass
class RepEventData:
    start_frame: int
    bottom_frame: int
    end_frame: int
    duration_sec: float | None
    minimum_knee_angle: float


@dataclass
class PartialRepEventData:
    start_frame: int
    end_frame: int
    reason: str


@dataclass
class RepCountResult:
    total_reps: int = 0
    rep_events: list[RepEventData] = field(default_factory=list)
    partial_rep_events: list[PartialRepEventData] = field(default_factory=list)
    ignored_partial_reps: int = 0
    confidence: float = 0.0
    phases: list[str] = field(default_factory=list)
    smoothed_angles: list[float] = field(default_factory=list)
    angle_stability: float = 0.0
    transition_clarity: float = 0.0


def _display_values(processed: list[float | None], raw: list[float]) -> list[float]:
    result: list[float] = []
    last = next((float(value) for value in processed if value is not None), 0.0)
    for index, value in enumerate(processed):
        if value is not None:
            last = float(value)
        elif index < len(raw):
            candidate = float(raw[index])
            if 20 <= candidate <= 180:
                last = candidate
        result.append(round(last, 2))
    return result


def _add_partial(
    events: list[PartialRepEventData],
    start_frame: int,
    end_frame: int,
    reason: str,
) -> None:
    """Aggregate nearby noisy failures rather than reporting every transition."""
    if events and start_frame - events[-1].end_frame <= PARTIAL_EVENT_MERGE_GAP_FRAMES:
        events[-1].end_frame = max(events[-1].end_frame, end_frame)
        if reason in {"low_confidence_segment", "too_long"}:
            events[-1].reason = reason
        return
    events.append(PartialRepEventData(start_frame, end_frame, reason))


def _aggregate_partials(
    partials: list[PartialRepEventData], completed: list[RepEventData]
) -> list[PartialRepEventData]:
    """Collapse repeated noisy candidates in the same between-rep interval."""
    if not partials:
        return []
    buckets: dict[int, PartialRepEventData] = {}
    priority = {"too_long": 4, "low_confidence_segment": 3, "did_not_return_to_standing": 2, "too_short": 1, "did_not_reach_depth": 0}
    for partial in partials:
        interval = sum(event.end_frame < partial.start_frame for event in completed)
        existing = buckets.get(interval)
        if existing is None:
            buckets[interval] = PartialRepEventData(partial.start_frame, partial.end_frame, partial.reason)
        else:
            existing.start_frame = min(existing.start_frame, partial.start_frame)
            existing.end_frame = max(existing.end_frame, partial.end_frame)
            if priority.get(partial.reason, 0) > priority.get(existing.reason, 0):
                existing.reason = partial.reason
    aggregated = [buckets[key] for key in sorted(buckets)]
    if len(aggregated) <= MAX_AGGREGATED_PARTIAL_EVENTS:
        return aggregated
    kept = aggregated[: MAX_AGGREGATED_PARTIAL_EVENTS - 1]
    overflow = aggregated[MAX_AGGREGATED_PARTIAL_EVENTS - 1 :]
    kept.append(
        PartialRepEventData(
            start_frame=overflow[0].start_frame,
            end_frame=overflow[-1].end_frame,
            reason="low_confidence_segment",
        )
    )
    return kept


def count_squat_reps(
    knee_angles: list[float],
    timestamps: list[float] | None = None,
    frame_indexes: list[int] | None = None,
    low_confidence_mask: list[bool] | None = None,
    pose_quality_score: float = 1.0,
    pose_detection_rate: float = 1.0,
) -> RepCountResult:
    if not knee_angles:
        return RepCountResult()

    indexes = frame_indexes or list(range(len(knee_angles)))
    processed = smooth_squat_angles(
        knee_angles,
        low_confidence_mask=low_confidence_mask,
        median_window=ANGLE_SMOOTHING_WINDOW,
    )
    display_angles = _display_values(processed, knee_angles)
    has_timing = bool(
        timestamps and len(timestamps) == len(knee_angles) and timestamps[-1] > timestamps[0]
    )
    phases = ["unreliable"] * len(knee_angles)
    events: list[RepEventData] = []
    partials: list[PartialRepEventData] = []
    clarity_values: list[float] = []

    state = "standing"
    standing_run = 0
    recent_standing_peak = 0.0
    start_pos: int | None = None
    bottom_pos: int | None = None
    minimum = 180.0
    standing_reference = 180.0
    descent_frames = 0
    bottom_frames = 0
    ascent_frames = 0
    last_rep_end_frame = -MIN_FRAMES_BETWEEN_REPS
    previous_angle: float | None = None

    def duration_at(position: int) -> float | None:
        if not has_timing or timestamps is None or start_pos is None:
            return None
        return float(timestamps[position] - timestamps[start_pos])

    def meaningful_excursion() -> float:
        return max(0.0, standing_reference - minimum)

    for position, sample in enumerate(processed):
        frame_index = indexes[position]
        continuity_break = bool(
            position > 0 and indexes[position] - indexes[position - 1] > MAX_INTERPOLATED_GAP_FRAMES + 1
        )
        if continuity_break or sample is None:
            if state != "standing" and start_pos is not None and meaningful_excursion() >= MIN_PARTIAL_MOVEMENT_DELTA_DEG:
                _add_partial(partials, indexes[start_pos], frame_index, "low_confidence_segment")
            state = "standing"
            standing_run = 0
            recent_standing_peak = 0.0
            start_pos = bottom_pos = None
            descent_frames = bottom_frames = ascent_frames = 0
            previous_angle = None
            continue

        angle = float(sample)
        delta = angle - previous_angle if previous_angle is not None else 0.0

        if state == "standing":
            phases[position] = "standing"
            if angle >= STANDING_KNEE_ANGLE_DEG:
                standing_run += 1
                recent_standing_peak = max(recent_standing_peak, angle)
            else:
                cooldown_ready = frame_index - last_rep_end_frame + 1 >= MIN_FRAMES_BETWEEN_REPS
                if (
                    standing_run >= MIN_PHASE_FRAMES
                    and cooldown_ready
                    and previous_angle is not None
                    and delta < -ANGLE_DIRECTION_EPSILON_DEG
                ):
                    state = "descending"
                    phases[position] = "descending"
                    start_pos = max(0, position - 1)
                    standing_reference = max(recent_standing_peak, previous_angle)
                    minimum = angle
                    descent_frames = 1
                    bottom_pos = None
                    bottom_frames = ascent_frames = 0
                standing_run = 0
                recent_standing_peak = 0.0

        elif state == "descending":
            phases[position] = "descending"
            descent_frames += 1
            minimum = min(minimum, angle)
            elapsed = duration_at(position)
            if elapsed is not None and elapsed > MAX_REP_DURATION_SEC:
                if meaningful_excursion() >= MIN_PARTIAL_MOVEMENT_DELTA_DEG and start_pos is not None:
                    _add_partial(partials, indexes[start_pos], frame_index, "too_long")
                state = "standing"
                standing_run = 1 if angle >= STANDING_KNEE_ANGLE_DEG else 0
                start_pos = bottom_pos = None
            elif (
                angle <= SQUAT_ATTEMPT_KNEE_ANGLE_DEG
                and meaningful_excursion() >= MIN_DEPTH_DELTA_DEG
                and descent_frames >= MIN_PHASE_FRAMES
            ):
                state = "bottom"
                phases[position] = "bottom"
                bottom_pos = position
                bottom_frames = 1
            elif angle >= STANDING_KNEE_ANGLE_DEG:
                if meaningful_excursion() >= MIN_PARTIAL_MOVEMENT_DELTA_DEG and start_pos is not None:
                    _add_partial(partials, indexes[start_pos], frame_index, "did_not_reach_depth")
                state = "standing"
                standing_run = 1
                recent_standing_peak = angle
                start_pos = bottom_pos = None

        elif state == "bottom":
            phases[position] = "bottom"
            if angle <= SQUAT_ATTEMPT_KNEE_ANGLE_DEG + 5:
                bottom_frames += 1
            if angle < minimum:
                minimum = angle
                bottom_pos = position
            elapsed = duration_at(position)
            if elapsed is not None and elapsed > MAX_REP_DURATION_SEC:
                if start_pos is not None:
                    _add_partial(partials, indexes[start_pos], frame_index, "too_long")
                state = "standing"
                standing_run = 0
                start_pos = bottom_pos = None
            elif angle >= minimum + ASCENT_HYSTERESIS_DEG and bottom_frames >= BOTTOM_HOLD_MIN_FRAMES:
                state = "ascending"
                phases[position] = "ascending"
                ascent_frames = 1

        else:  # ascending
            phases[position] = "ascending"
            ascent_frames += 1
            if angle < minimum:
                minimum = angle
                bottom_pos = position
            if angle >= STANDING_KNEE_ANGLE_DEG and ascent_frames >= MIN_PHASE_FRAMES:
                start = start_pos if start_pos is not None else 0
                duration = duration_at(position)
                reason = None
                if duration is not None and duration < MIN_REP_DURATION_SEC:
                    reason = "too_short"
                elif duration is not None and duration > MAX_REP_DURATION_SEC:
                    reason = "too_long"
                if reason is None and bottom_pos is not None:
                    events.append(
                        RepEventData(
                            start_frame=indexes[start],
                            bottom_frame=indexes[bottom_pos],
                            end_frame=frame_index,
                            duration_sec=round(duration, 3) if duration is not None else None,
                            minimum_knee_angle=round(minimum, 2),
                        )
                    )
                    excursion_clarity = min(1.0, meaningful_excursion() / MIN_DEPTH_DELTA_DEG)
                    phase_clarity = min(1.0, descent_frames / MIN_PHASE_FRAMES) * min(
                        1.0, ascent_frames / MIN_PHASE_FRAMES
                    )
                    clarity_values.append((excursion_clarity + phase_clarity) / 2)
                    last_rep_end_frame = frame_index
                elif start_pos is not None:
                    _add_partial(partials, indexes[start_pos], frame_index, reason or "did_not_return_to_standing")
                state = "standing"
                standing_run = 1
                recent_standing_peak = angle
                start_pos = bottom_pos = None
                descent_frames = bottom_frames = ascent_frames = 0

        previous_angle = angle

    if state != "standing" and start_pos is not None and meaningful_excursion() >= MIN_PARTIAL_MOVEMENT_DELTA_DEG:
        reason = "did_not_return_to_standing" if bottom_pos is not None else "did_not_reach_depth"
        _add_partial(partials, indexes[start_pos], indexes[-1], reason)

    partials = _aggregate_partials(partials, events)
    complete = len(events)
    partial_count = len(partials)
    stability = compute_angle_stability(processed)
    transition_clarity = mean(clarity_values) if clarity_values else 0.0
    if complete == 0:
        confidence = 0.0
    else:
        complete_ratio = complete / (complete + partial_count)
        pose_factor = (0.7 * max(0.0, min(1.0, pose_quality_score))) + (
            0.3 * max(0.0, min(1.0, pose_detection_rate))
        )
        durations = [event.duration_sec for event in events if event.duration_sec is not None]
        if len(durations) > 1 and mean(durations) > 0:
            duration_consistency = max(0.0, 1 - min(1.0, pstdev(durations) / mean(durations)))
        elif durations:
            duration_consistency = 0.9
        else:
            duration_consistency = 0.85
        confidence = (
            (0.30 * complete_ratio)
            + (0.20 * pose_factor)
            + (0.20 * stability)
            + (0.15 * transition_clarity)
            + (0.15 * duration_consistency)
        )

    return RepCountResult(
        total_reps=complete,
        rep_events=events,
        partial_rep_events=partials,
        ignored_partial_reps=partial_count,
        confidence=round(max(0.0, min(1.0, confidence)), 3),
        phases=phases,
        smoothed_angles=display_angles,
        angle_stability=stability,
        transition_clarity=round(transition_clarity, 3),
    )
