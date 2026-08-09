import pytest

from app.services import exercise_recognition_service as service


def test_service_returns_not_available_without_model(tmp_path, monkeypatch):
    monkeypatch.setattr(service, "RECOGNITION_MODELS_DIR", tmp_path / "missing")
    result = service.predict_exercise_from_features({"f1": 1.0})
    assert result["status"] == "not_available"
    assert result["experimental"] is True


def test_formatted_result_requires_confirmation_and_reports_registered_analyzer():
    result = service.format_recognition_result({
        "status": "success", "suggested_exercise_id": "knee_extension", "confidence": 0.82,
        "top_predictions": [{"exercise_id": "knee_extension", "confidence": 0.82}],
    })
    assert result["experimental"] is True
    assert result["analyzer_available"] is True
    assert result["requires_manual_confirmation"] is True
    assert result["suggestion_actionable"] is True
    assert result["can_auto_route"] is False
    assert "Manual exercise selection remains primary." in result["limitations"]


def test_sequence_prediction_uses_torchscript_candidate(monkeypatch):
    torch = pytest.importorskip("torch")

    class FakeSequenceModel:
        def __call__(self, values):
            assert tuple(values.shape) == (1, 4, 2)
            return torch.tensor([[0.1, 2.0]])

    metadata = {
        "artifact_format": "torchscript_sequence",
        "feature_columns": ["f1", "f2"],
        "sequence_length": 4,
        "feature_mean": [0.0, 0.0],
        "feature_std": [1.0, 1.0],
        "classes": ["bodyweight_squat", "push_up"],
    }
    monkeypatch.setattr(
        service,
        "load_recognition_model",
        lambda model_id=None, required_format=None: {
            "estimator": FakeSequenceModel(), "metadata": metadata
        },
    )
    result = service.predict_exercise_from_sequence([{"f1": 1.0, "f2": 2.0}])
    assert result["status"] == "success"
    assert result["suggested_exercise_id"] == "push_up"
    assert result["requires_manual_confirmation"] is True


def test_sequence_prediction_abstains_below_calibrated_threshold(monkeypatch):
    torch = pytest.importorskip("torch")

    class FakeSequenceModel:
        def __call__(self, values):
            return torch.tensor([[0.1, 0.2]])

    monkeypatch.setattr(
        service,
        "load_recognition_model",
        lambda model_id=None, required_format=None: {
            "estimator": FakeSequenceModel(),
            "metadata": {
                "artifact_format": "torchscript_sequence",
                "feature_columns": ["f1"],
                "sequence_length": 4,
                "feature_mean": [0.0],
                "feature_std": [1.0],
                "classes": ["bodyweight_squat", "push_up"],
                "temperature": 1.0,
                "confidence_threshold": 0.8,
            },
        },
    )
    result = service.predict_exercise_from_sequence([{"f1": 1.0}])
    assert result["status"] == "uncertain"
    assert result["suggestion_actionable"] is False
    assert result["confidence_threshold"] == 0.8


def test_unsupported_recognition_is_not_actionable():
    result = service.format_recognition_result({
        "status": "success", "suggested_exercise_id": "hammer_curl", "confidence": 0.9,
    })
    assert result["analyzer_available"] is False
    assert result["suggestion_actionable"] is False
