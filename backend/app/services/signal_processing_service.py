"""Dependency-free preprocessing for pose-derived squat angle signals."""

from __future__ import annotations

import math
from statistics import mean, median

from app.core.exercise_thresholds import (
    ANGLE_JUMP_THRESHOLD_DEG,
    MAX_INTERPOLATED_GAP_FRAMES,
    MAX_VALID_JOINT_ANGLE_DEG,
    MIN_VALID_JOINT_ANGLE_DEG,
)

AngleSample = float | None


def _coerce(value: float | None) -> AngleSample:
    if value is None:
        return None
    number = float(value)
    if not math.isfinite(number):
        return None
    if not MIN_VALID_JOINT_ANGLE_DEG <= number <= MAX_VALID_JOINT_ANGLE_DEG:
        return None
    return number


def remove_angle_spikes(
    values: list[float | None], jump_threshold: float = ANGLE_JUMP_THRESHOLD_DEG
) -> list[AngleSample]:
    """Remove impossible values and isolated one-frame angle jumps."""
    clean = [_coerce(value) for value in values]
    result = list(clean)
    for index in range(1, len(clean) - 1):
        previous, current, following = clean[index - 1], clean[index], clean[index + 1]
        if previous is None or current is None or following is None:
            continue
        if (
            abs(current - previous) > jump_threshold
            and abs(current - following) > jump_threshold
            and abs(previous - following) <= jump_threshold
        ):
            result[index] = None
    return result


def interpolate_short_gaps(
    values: list[float | None], max_gap: int = MAX_INTERPOLATED_GAP_FRAMES
) -> list[AngleSample]:
    """Interpolate bounded internal gaps; preserve longer gaps as continuity breaks."""
    result = [_coerce(value) for value in values]
    index = 0
    while index < len(result):
        if result[index] is not None:
            index += 1
            continue
        start = index
        while index < len(result) and result[index] is None:
            index += 1
        end = index
        gap = end - start
        left = result[start - 1] if start > 0 else None
        right = result[end] if end < len(result) else None
        if gap <= max_gap and left is not None and right is not None:
            for offset in range(1, gap + 1):
                result[start + offset - 1] = left + ((right - left) * offset / (gap + 1))
    return result


def _smooth_valid_segment(values: list[float], median_window: int, average_window: int) -> list[float]:
    if len(values) < max(7, median_window + 2):
        return values
    median_radius = max(0, median_window // 2)
    medians = [
        float(median(values[max(0, i - median_radius) : min(len(values), i + median_radius + 1)]))
        for i in range(len(values))
    ]
    average_radius = max(0, average_window // 2)
    return [
        mean(medians[max(0, i - average_radius) : min(len(medians), i + average_radius + 1)])
        for i in range(len(medians))
    ]


def smooth_squat_angles(
    values: list[float | None],
    low_confidence_mask: list[bool] | None = None,
    median_window: int = 5,
    average_window: int = 3,
) -> list[AngleSample]:
    """Filter spikes, suppress low-quality samples, interpolate short gaps, and smooth segments."""
    filtered = remove_angle_spikes(values)
    if low_confidence_mask and len(low_confidence_mask) == len(filtered):
        filtered = [None if low_confidence_mask[i] else value for i, value in enumerate(filtered)]
    interpolated = interpolate_short_gaps(filtered)
    result: list[AngleSample] = list(interpolated)
    index = 0
    while index < len(result):
        if result[index] is None:
            index += 1
            continue
        start = index
        segment: list[float] = []
        while index < len(result) and result[index] is not None:
            segment.append(float(result[index]))
            index += 1
        result[start:index] = _smooth_valid_segment(segment, median_window, average_window)
    return result


def compute_angle_stability(values: list[float | None]) -> float:
    """Return 0–1 stability from adjacent valid-frame changes."""
    changes = [
        abs(float(right) - float(left))
        for left, right in zip(values, values[1:])
        if left is not None and right is not None
    ]
    if not changes:
        return 0.0
    average_change = mean(changes)
    large_jump_ratio = sum(change > 20 for change in changes) / len(changes)
    score = 1 - min(1.0, average_change / 20) - (0.25 * large_jump_ratio)
    return round(max(0.0, min(1.0, score)), 3)


def _finite_series(values: list[float | None]) -> list[float]:
    """Compatibility filler for consumers that require one numeric value per frame."""
    if not values:
        return []
    result = [float(value) if value is not None and math.isfinite(float(value)) else math.nan for value in values]
    valid = [index for index, value in enumerate(result) if math.isfinite(value)]
    if not valid:
        return [0.0] * len(result)
    for index, value in enumerate(result):
        if math.isfinite(value):
            continue
        left = max((item for item in valid if item < index), default=None)
        right = min((item for item in valid if item > index), default=None)
        if left is None:
            result[index] = result[right]  # type: ignore[index]
        elif right is None:
            result[index] = result[left]
        else:
            fraction = (index - left) / (right - left)
            result[index] = result[left] + ((result[right] - result[left]) * fraction)
    return result


def moving_average(values: list[float], window_size: int = 5) -> list[float]:
    clean = _finite_series(values)
    if not clean:
        return []
    radius = max(0, int(window_size) // 2)
    return [mean(clean[max(0, i - radius) : min(len(clean), i + radius + 1)]) for i in range(len(clean))]


def rolling_median(values: list[float], window_size: int = 5) -> list[float]:
    clean = _finite_series(values)
    if not clean:
        return []
    radius = max(0, int(window_size) // 2)
    return [float(median(clean[max(0, i - radius) : min(len(clean), i + radius + 1)])) for i in range(len(clean))]


def smooth_angle_series(values: list[float], window_size: int = 5) -> list[float]:
    """Backward-compatible numeric wrapper around the squat preprocessor."""
    return _finite_series(smooth_squat_angles(values, median_window=window_size))
