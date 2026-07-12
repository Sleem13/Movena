import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from predict_squat_baseline_v2 import predict_rows_v2
from test_train_squat_baseline_v2 import dummy_v2
from train_squat_baseline_v2 import train_baselines_v2


def test_v2_prediction_has_candidate_version_and_warning(tmp_path):
    data = tmp_path / "v2.csv"
    dummy_v2(data)
    model_dir = tmp_path / "models"
    train_baselines_v2(data, model_dir, tmp_path / "missing-old.json")

    result = predict_rows_v2(
        model_dir / "artifacts/squat_quality_baseline_v2.pkl", data, "squat_correct-test.mp4"
    )[0]

    assert result["predicted_label"]
    assert 0 <= result["confidence"] <= 1
    assert result["model_version"] == "sprint_7_baseline_v2"
    assert "not clinically validated" in result["warning"].lower()
