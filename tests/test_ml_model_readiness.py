import pytest
from fastapi.testclient import TestClient

from backend.app.main import app
from app.services import ml_model_readiness_service as service


client = TestClient(app)


def test_ml_readiness_endpoint_has_an_entry_for_each_supported_exercise():
    response = client.get("/api/v1/ml/readiness")

    assert response.status_code == 200
    payload = response.json()
    assert isinstance(payload["feature_enabled"], bool)
    assert any(item["exercise_id"] == "bodyweight_squat" for item in payload["models"])
    assert any(item["status"] == "not_configured" for item in payload["models"])


def test_required_model_validation_fails_closed(monkeypatch):
    monkeypatch.setattr(
        service,
        "ml_model_readiness",
        lambda: {"models": [{"exercise_id": "sit_to_stand", "status": "blocked", "reason": "Approval missing."}]},
    )

    with pytest.raises(RuntimeError, match="sit_to_stand: Approval missing"):
        service.validate_required_ml_models(["sit_to_stand"])
