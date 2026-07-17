from app.exercises.shoulder_abduction.state_machine import count_shoulder_abduction_reps


def complete_cycle():
    return [25] * 5 + [30, 45, 60, 78, 85, 90, 90, 88] + [70, 50, 35, 30, 25, 25, 25]


def test_lowered_raised_lowered_counts_one_rep():
    angles = complete_cycle()
    result = count_shoulder_abduction_reps(angles, [index * .1 for index in range(len(angles))])
    assert result.total_reps == 1
    assert result.rep_events[0].maximum_angle >= 75
    assert any("raised" in transition for transition in result.phase_transitions)


def test_partial_raise_is_ignored():
    result = count_shoulder_abduction_reps([25] * 5 + [35, 50, 68, 68, 55, 35, 25, 25, 25])
    assert result.total_reps == 0
    assert result.ignored_partial_reps >= 1
