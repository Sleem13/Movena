from app.exercises.knee_extension.state_machine import count_knee_extension_reps


def complete_cycle():
    return [100] * 5 + [110, 125, 140, 150, 158, 165, 170, 170, 168] + [155, 145, 130, 115, 105, 100, 100]


def test_flexed_extended_flexed_cycle_counts_one_rep():
    angles = complete_cycle()
    result = count_knee_extension_reps(angles, [index * 0.1 for index in range(len(angles))])
    assert result.total_reps == 1
    assert result.valid_reps == 1
    assert result.rep_events[0].maximum_knee_angle >= 155
    assert any("extended" in transition for transition in result.phase_transitions)


def test_partial_extension_is_not_counted():
    result = count_knee_extension_reps([100] * 5 + [115, 135, 150, 150, 140, 120, 100, 100, 100])
    assert result.total_reps == 0
    assert result.ignored_partial_reps >= 1
