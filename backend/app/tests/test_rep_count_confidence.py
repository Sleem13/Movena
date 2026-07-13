from app.services.rep_counting_service import count_squat_reps
from app.tests.test_rep_count_state_machine import one_rep, timed


def test_stable_complete_reps_have_high_confidence():
    values = one_rep() * 5
    result = count_squat_reps(values, timed(values), pose_quality_score=0.95, pose_detection_rate=0.95)
    assert result.total_reps == 5
    assert result.confidence >= 0.65


def test_meaningful_partials_reduce_rep_confidence():
    clean_values = one_rep() * 2
    partial = [170] * 6 + [150, 140, 150, 170] + [170] * 10
    noisy_values = clean_values + partial + partial
    clean = count_squat_reps(clean_values, timed(clean_values))
    noisy = count_squat_reps(noisy_values, timed(noisy_values))
    assert noisy.total_reps == clean.total_reps
    assert 1 <= noisy.ignored_partial_reps <= 2
    assert noisy.confidence < clean.confidence


def test_no_complete_reps_have_zero_confidence():
    values = [170, 168, 165, 162, 165, 168, 170] * 5
    result = count_squat_reps(values, timed(values))
    assert result.total_reps == 0
    assert result.confidence == 0
