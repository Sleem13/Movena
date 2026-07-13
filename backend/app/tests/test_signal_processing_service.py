import math

from app.services.signal_processing_service import moving_average, rolling_median, smooth_angle_series


def test_noisy_angle_sequence_is_smoothed_without_length_change():
    values = [170, 169, 171, 140, 90, 300, 92, 140, 169, 170]
    smoothed = smooth_angle_series(values)
    assert len(smoothed) == len(values)
    assert max(smoothed) < 250
    assert abs(smoothed[5] - smoothed[4]) < abs(values[5] - values[4])


def test_filters_handle_empty_and_nan_values():
    assert moving_average([]) == []
    assert rolling_median([]) == []
    result = smooth_angle_series([170, math.nan, 150, None, 120, 150, 170])  # type: ignore[list-item]
    assert len(result) == 7
    assert all(math.isfinite(value) for value in result)
