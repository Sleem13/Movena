import sys
from pathlib import Path

import pandas as pd
import pytest


REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "scripts"))

from predict_squat_baseline import predict_rows
from test_train_squat_baseline import dummy_training_data
from train_squat_baseline import train_baselines


def test_prediction_shape_and_experimental_warning(tmp_path):
    input_path = tmp_path / "features.csv"
    model_dir = tmp_path / "models"
    dummy_training_data(input_path)
    train_baselines(input_path, model_dir)

    result = predict_rows(model_dir / "artifacts/squat_quality_baseline.pkl", input_path, "squat_correct-holdout.mp4")

    assert len(result) == 1
    assert set(result[0]) == {"video_path", "predicted_label", "confidence", "model_name", "model_version", "warning"}
    assert 0 <= result[0]["confidence"] <= 1
    assert "not clinically validated" in result[0]["warning"].lower()


def test_prediction_fails_gracefully_when_model_is_missing(tmp_path):
    input_path = tmp_path / "features.csv"
    pd.DataFrame([{"feature_a": 1}]).to_csv(input_path, index=False)
    with pytest.raises(FileNotFoundError, match="Run train_squat_baseline.py first"):
        predict_rows(tmp_path / "missing.pkl", input_path)
