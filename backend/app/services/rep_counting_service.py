"""State-machine squat repetition counting over a smoothed knee-angle signal."""

from __future__ import annotations

from dataclasses import dataclass, field

from app.core.exercise_thresholds import (
    ANGLE_DIRECTION_EPSILON_DEG,
    ANGLE_SMOOTHING_WINDOW,
    BOTTOM_HOLD_MIN_FRAMES,
    MAX_REP_DURATION_SEC,
    MIN_DEPTH_DELTA_DEG,
    MIN_FRAMES_BETWEEN_REPS,
    MIN_REP_DURATION_SEC,
    SQUAT_DEPTH_KNEE_ANGLE_DEG,
    STANDING_KNEE_ANGLE_DEG,
)
from app.services.signal_processing_service import smooth_angle_series


@dataclass
class RepEventData:
    start_frame: int
    bottom_frame: int
    end_frame: int
    duration_sec: float | None
    minimum_knee_angle: float


@dataclass
class RepCountResult:
    total_reps: int = 0
    rep_events: list[RepEventData] = field(default_factory=list)
    ignored_partial_reps: int = 0
    confidence: float = 0.0
    phases: list[str] = field(default_factory=list)
    smoothed_angles: list[float] = field(default_factory=list)


def count_squat_reps(
    knee_angles: list[float],
    timestamps: list[float] | None = None,
    frame_indexes: list[int] | None = None,
) -> RepCountResult:
    if not knee_angles:
        return RepCountResult()

    angles = smooth_angle_series(knee_angles, ANGLE_SMOOTHING_WINDOW)
    indexes = frame_indexes or list(range(len(angles)))
    has_timing = bool(
        timestamps
        and len(timestamps) == len(angles)
        and timestamps[-1] > timestamps[0]
    )
    phases: list[str] = []
    events: list[RepEventData] = []
    ignored = 0
    state = "standing"
    start_index: int | None = None
    bottom_index: int | None = None
    bottom_frames = 0
    standing_peak = angles[0]
    minimum = angles[0]
    last_rep_end = -MIN_FRAMES_BETWEEN_REPS

    # Preserve support for very short, already accepted clips while applying
    # the configured hold and spacing checks to normal recordings.
    required_bottom_frames = 1 if len(angles) < MIN_FRAMES_BETWEEN_REPS else BOTTOM_HOLD_MIN_FRAMES
    required_gap = 1 if len(angles) < MIN_FRAMES_BETWEEN_REPS else MIN_FRAMES_BETWEEN_REPS

    for index, angle in enumerate(angles):
        previous = angles[index - 1] if index else angle
        delta = angle - previous
        standing_peak = max(standing_peak, angle)

        if state == "standing":
            phases.append("standing")
            if angle < STANDING_KNEE_ANGLE_DEG and delta < -ANGLE_DIRECTION_EPSILON_DEG:
                state = "descending"
                start_index = index - 1 if index else 0
                standing_peak = max(angles[start_index], standing_peak)
                minimum = angle
        elif state == "descending":
            phases.append("descending")
            minimum = min(minimum, angle)
            if angle <= SQUAT_DEPTH_KNEE_ANGLE_DEG and standing_peak - minimum >= MIN_DEPTH_DELTA_DEG:
                state = "bottom"
                bottom_index = index
                bottom_frames = 1
            elif angle >= STANDING_KNEE_ANGLE_DEG:
                ignored += 1
                state = "standing"
                start_index = None
        elif state == "bottom":
            phases.append("bottom")
            if angle <= SQUAT_DEPTH_KNEE_ANGLE_DEG + 5:
                bottom_frames += 1
                if angle < minimum:
                    minimum = angle
                    bottom_index = index
            if delta > ANGLE_DIRECTION_EPSILON_DEG and bottom_frames >= required_bottom_frames:
                state = "ascending"
        else:  # ascending
            phases.append("ascending")
            if angle >= STANDING_KNEE_ANGLE_DEG:
                start = start_index if start_index is not None else 0
                duration = (
                    float(timestamps[index] - timestamps[start]) if has_timing and timestamps else None
                )
                duration_valid = duration is None or MIN_REP_DURATION_SEC <= duration <= MAX_REP_DURATION_SEC
                spacing_valid = indexes[index] - last_rep_end >= required_gap
                if duration_valid and spacing_valid and bottom_index is not None:
                    events.append(
                        RepEventData(
                            start_frame=indexes[start],
                            bottom_frame=indexes[bottom_index],
                            end_frame=indexes[index],
                            duration_sec=round(duration, 3) if duration is not None else None,
                            minimum_knee_angle=round(minimum, 2),
                        )
                    )
                    last_rep_end = indexes[index]
                else:
                    ignored += 1
                state = "standing"
                start_index = None
                bottom_index = None
                bottom_frames = 0
                standing_peak = angle
            elif delta < -ANGLE_DIRECTION_EPSILON_DEG:
                # A second descent before standing is a partial/irregular cycle.
                ignored += 1
                state = "descending"
                start_index = index - 1
                minimum = angle

    if state != "standing":
        ignored += 1

    complete = len(events)
    confidence = complete / (complete + ignored) if complete + ignored else 0.5
    if complete:
        duration_quality = sum(
            1 for event in events if event.duration_sec is None or 1.0 <= event.duration_sec <= 6.0
        ) / complete
        confidence = (confidence * 0.75) + (duration_quality * 0.25)

    return RepCountResult(
        total_reps=complete,
        rep_events=events,
        ignored_partial_reps=ignored,
        confidence=round(max(0.0, min(1.0, confidence)), 3),
        phases=phases,
        smoothed_angles=[round(value, 2) for value in angles],
    )
