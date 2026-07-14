import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "backend"))

from app.exercises.sit_to_stand.state_machine import count_sit_to_stand_reps


def cycle():
    return [90] * 5 + [105, 120, 135, 150, 160, 165] + [165] * 4 + [150, 135, 120, 105, 95, 90] + [90] * 5


def test_clean_three_rep_sequence_counts_three():
    values = cycle() * 3
    result = count_sit_to_stand_reps(values, values, [i / 10 for i in range(len(values))])
    assert result.total_reps == 3
    assert result.ignored_partial_reps == 0
    assert len(result.rep_events) == 3


def test_small_noise_still_counts_three():
    values = cycle() * 3
    noisy = [value + ((index % 3) - 1) * 1.5 for index, value in enumerate(values)]
    result = count_sit_to_stand_reps(noisy, noisy, [i / 10 for i in range(len(noisy))])
    assert result.total_reps == 3


def test_partial_rise_is_not_counted():
    values = [90] * 6 + [105, 120, 130, 125, 110, 95] + [90] * 6
    result = count_sit_to_stand_reps(values, values, [i / 10 for i in range(len(values))])
    assert result.total_reps == 0
    assert result.ignored_partial_reps >= 1
