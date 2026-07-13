import random

from app.services.rep_counting_service import count_squat_reps


def one_rep():
    return [170] * 6 + [155, 145, 135, 125] + [110, 105, 108] + [125, 140, 155, 165] + [170] * 4


def timed(values):
    return [index / 10 for index in range(len(values))]


def test_clean_eight_rep_sequence_counts_eight():
    values = one_rep() * 8
    result = count_squat_reps(values, timed(values))
    assert result.total_reps == 8
    assert result.ignored_partial_reps == 0
    assert result.confidence >= 0.85
    assert all(0.8 <= event.duration_sec <= 8 for event in result.rep_events)


def test_noisy_eight_rep_sequence_still_counts_eight():
    random.seed(7)
    values = [value + random.uniform(-4, 4) for value in one_rep() * 8]
    result = count_squat_reps(values, timed(values))
    assert result.total_reps == 8


def test_tiny_knee_movement_does_not_count():
    values = ([170, 168, 165, 162, 165, 168, 170] * 4)
    assert count_squat_reps(values, timed(values)).total_reps == 0


def test_partial_rep_is_ignored():
    values = [170] * 6 + [155, 140, 125, 110, 105]
    result = count_squat_reps(values, timed(values))
    assert result.total_reps == 0
    assert result.ignored_partial_reps == 1
