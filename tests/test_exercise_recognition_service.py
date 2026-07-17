from app.services import exercise_recognition_service as service


def test_service_returns_not_available_without_model(tmp_path, monkeypatch):
    monkeypatch.setattr(service, "RECOGNITION_MODELS_DIR", tmp_path / "missing")
    result = service.predict_exercise_from_features({"f1": 1.0})
    assert result["status"] == "not_available"
    assert result["experimental"] is True


def test_formatted_result_requires_confirmation_and_blocks_unsupported_analyzer():
    result = service.format_recognition_result({
        "status": "success", "suggested_exercise_id": "knee_extension", "confidence": 0.82,
        "top_predictions": [{"exercise_id": "knee_extension", "confidence": 0.82}],
    })
    assert result["experimental"] is True
    assert result["analyzer_available"] is False
    assert result["requires_manual_confirmation"] is True
    assert result["can_auto_route"] is False
    assert "Manual exercise selection remains primary." in result["limitations"]

