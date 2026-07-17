from app.exercises.hip_abduction.state_machine import count_hip_abduction_reps


def complete_cycle():
    return [8] * 5 + [12, 18, 24, 28, 32, 35, 35, 33] + [25, 18, 12, 9, 8, 8, 8]


def test_neutral_abducted_neutral_counts_one_rep():
    angles = complete_cycle()
    result = count_hip_abduction_reps(angles, [index * .1 for index in range(len(angles))])
    assert result.total_reps == 1
    assert result.rep_events[0].maximum_angle >= 25
    assert any("abducted" in transition for transition in result.phase_transitions)


def test_partial_abduction_is_ignored():
    result = count_hip_abduction_reps([8] * 5 + [12, 18, 22, 22, 18, 12, 8, 8, 8])
    assert result.total_reps == 0
    assert result.ignored_partial_reps >= 1
