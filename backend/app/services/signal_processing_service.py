"""Small, dependency-free filters for noisy pose-derived angle signals."""

from __future__ import annotations

import math
from statistics import median


def _finite_series(values: list[float]) -> list[float]:
    if not values:
        return []
    result = [float(value) if value is not None else math.nan for value in values]
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
    """Return a centered moving average with the same length as the input."""
    clean = _finite_series(values)
    if not clean:
        return []
    window_size = max(1, int(window_size))
    radius = window_size // 2
    return [
        sum(clean[max(0, index - radius) : min(len(clean), index + radius + 1)])
        / len(clean[max(0, index - radius) : min(len(clean), index + radius + 1)])
        for index in range(len(clean))
    ]


def rolling_median(values: list[float], window_size: int = 5) -> list[float]:
    """Return a centered rolling median with finite-value interpolation."""
    clean = _finite_series(values)
    if not clean:
        return []
    window_size = max(1, int(window_size))
    radius = window_size // 2
    return [
        float(median(clean[max(0, index - radius) : min(len(clean), index + radius + 1)]))
        for index in range(len(clean))
    ]


def smooth_angle_series(values: list[float], window_size: int = 5) -> list[float]:
    """Suppress isolated spikes, then soften residual frame-to-frame jitter."""
    clean = _finite_series(values)
    # Very short clips cannot support a meaningful temporal filter. Returning
    # the sanitized signal avoids erasing their only bottom-position sample.
    if len(clean) < max(7, window_size + 2):
        return clean
    return moving_average(rolling_median(clean, window_size), 3)
