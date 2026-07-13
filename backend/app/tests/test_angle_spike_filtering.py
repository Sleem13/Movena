import math

from app.services.signal_processing_service import (
    compute_angle_stability,
    interpolate_short_gaps,
    remove_angle_spikes,
    smooth_squat_angles,
)


def test_isolated_large_angle_spike_is_removed_and_interpolated():
    values = [170, 168, 166, 45, 164, 160, 155]
    filtered = remove_angle_spikes(values)
    assert filtered[3] is None
    interpolated = interpolate_short_gaps(filtered)
    assert interpolated[3] == 165


def test_impossible_and_nan_values_become_gaps():
    result = remove_angle_spikes([170, 190, math.nan, 10, 165])
    assert result[1:4] == [None, None, None]


def test_long_gap_is_not_interpolated_and_breaks_continuity():
    values = [170, 165, None, None, None, None, 140, 130]
    result = smooth_squat_angles(values)
    assert result[2:6] == [None, None, None, None]


def test_stable_signal_has_higher_stability_than_jittery_signal():
    stable = compute_angle_stability([170, 168, 165, 160, 155])
    jittery = compute_angle_stability([170, 130, 175, 125, 170])
    assert stable > jittery
