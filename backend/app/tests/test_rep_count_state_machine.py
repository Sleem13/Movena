import random

from app.services.rep_counting_service import count_squat_reps


def one_rep():
    return [170] * 6 + [155, 145, 135, 125] + [110, 105, 108] + [125, 140, 155, 165] + [170] * 4


def timed(values):
    return [index / 10 for index in range(len(values))]


def test_clean_five_rep_sequence_counts_five():
    values = one_rep() * 5
    result = count_squat_reps(values, timed(values))
    assert result.total_reps == 5
    assert result.ignored_partial_reps == 0
    assert result.confidence >= 0.85
    assert all(0.8 <= event.duration_sec <= 8 for event in result.rep_events)


def test_noisy_five_rep_sequence_still_counts_five():
    random.seed(7)
    values = [value + random.uniform(-4, 4) for value in one_rep() * 5]
    result = count_squat_reps(values, timed(values))
    assert result.total_reps == 5


def test_one_rep_counts_when_upright_angle_is_just_under_160_degrees():
    values = [159] * 6 + [150, 140, 125, 105, 105, 108, 125, 140, 150] + [159] * 6
    result = count_squat_reps(values, timed(values))
    assert result.total_reps == 1
    assert result.ignored_partial_reps == 0


def test_tiny_knee_movement_does_not_count():
    values = ([170, 168, 165, 162, 165, 168, 170] * 4)
    result = count_squat_reps(values, timed(values))
    assert result.total_reps == 0
    assert result.ignored_partial_reps == 0


def test_partial_rep_is_ignored():
    values = [170] * 6 + [155, 140, 125, 110, 105]
    result = count_squat_reps(values, timed(values))
    assert result.total_reps == 0
    assert result.ignored_partial_reps == 1


def test_one_complete_rep_plus_repeated_jitter_does_not_create_many_partials():
    values = one_rep() + ([170, 150, 168, 149, 170] * 10)
    result = count_squat_reps(values, timed(values))
    assert result.total_reps == 1
    assert result.ignored_partial_reps <= 1


def test_long_low_confidence_gap_breaks_continuity_without_overcounting():
    values = one_rep() + one_rep()
    mask = [False] * len(values)
    mask[8:16] = [True] * 8
    result = count_squat_reps(values, timed(values), low_confidence_mask=mask)
    assert result.total_reps <= 1
    assert result.ignored_partial_reps <= 1
    assert all(event.reason in {"low_confidence_segment", "did_not_return_to_standing"} for event in result.partial_rep_events)
