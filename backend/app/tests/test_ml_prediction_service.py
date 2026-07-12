from pathlib import Path

from app.services.ml_prediction_service import (
    EXPERIMENTAL_WARNING,
    predict_experimental_quality,
)


def point(x, y):
    return {"x": x, "y": y, "z": 0.0, "visibility": 0.95}


def sample_frames():
    landmarks = {
        "left_shoulder": point(0.40, 0.20), "right_shoulder": point(0.60, 0.20),
        "left_hip": point(0.42, 0.50), "right_hip": point(0.58, 0.50),
        "left_knee": point(0.42, 0.70), "right_knee": point(0.58, 0.70),
        "left_ankle": point(0.52, 0.85), "right_ankle": point(0.48, 0.85),
    }
    return [{"frame_index": index, "landmarks": landmarks} for index in range(3)]


def test_saved_model_prediction_shape_and_warning():
    result = predict_experimental_quality(sample_frames())
    assert result.enabled is True
    assert result.predicted_label
    assert result.model_name == "svc_rbf"
    assert result.model_version == "sprint_5_baseline"
    assert result.confidence is None or 0 <= result.confidence <= 1
    assert result.warning == EXPERIMENTAL_WARNING
    assert "diagnos" not in result.warning.lower()


def test_missing_model_artifacts_fail_gracefully(tmp_path):
    result = predict_experimental_quality(
        sample_frames(),
        tmp_path / "missing.pkl",
        tmp_path / "missing-features.json",
        tmp_path / "missing-labels.json",
    )
    assert result.enabled is False
    assert result.predicted_label is None
    assert result.confidence is None
    assert "rule-based analysis is still available" in result.warning.lower()
