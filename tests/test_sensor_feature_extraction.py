import math
import sys
from pathlib import Path

import pytest

pd = pytest.importorskip("pandas")

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT / "scripts") not in sys.path:
    sys.path.insert(0, str(REPO_ROOT / "scripts"))

from extract_sensor_features import extract_features, rms, signal_energy


def test_rms_and_energy_calculation():
    series = pd.Series([1, 2, 3, 4])

    assert rms(series) == pytest.approx(math.sqrt(7.5))
    assert signal_energy(series) == pytest.approx(30.0)


def test_sliding_window_feature_extraction_on_dummy_data(tmp_path):
    input_path = tmp_path / "processed_sensor.csv"
    output_path = tmp_path / "window_features.csv"
    dataframe = pd.DataFrame(
        {
            "source_dataset": ["uci_physical_therapy_exercises"] * 6,
            "source_file": ["dummy.txt"] * 6,
            "subject_id": ["s1"] * 6,
            "exercise_id": ["e1"] * 6,
            "execution_type": ["u1"] * 6,
            "split": ["test"] * 6,
            "sample_index": list(range(6)),
            "acc_x": [1, 2, 3, 4, 5, 6],
            "gyro_y": [2, 2, 2, 2, 2, 2],
        }
    )
    dataframe.to_csv(input_path, index=False)

    created = extract_features(input_path, output_path, window_size=4, step_size=2)
    features = pd.read_csv(created)

    assert created == output_path
    assert len(features) == 2
    assert features.loc[0, "acc_x_mean"] == pytest.approx(2.5)
    assert features.loc[0, "acc_x_min"] == pytest.approx(1)
    assert features.loc[0, "acc_x_max"] == pytest.approx(4)
    assert features.loc[0, "acc_x_range"] == pytest.approx(3)
    assert features.loc[0, "acc_x_energy"] == pytest.approx(30)
    assert features.loc[0, "gyro_y_rms"] == pytest.approx(2)


def test_missing_input_file_handling(tmp_path):
    missing_path = tmp_path / "missing.csv"

    with pytest.raises(FileNotFoundError):
        extract_features(missing_path, tmp_path / "out.csv")
