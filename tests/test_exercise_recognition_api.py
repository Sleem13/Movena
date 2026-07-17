from fastapi.testclient import TestClient

from app.main import app
from app.services import exercise_recognition_service as service


client = TestClient(app)


def test_recognition_api_is_safe_without_model(tmp_path, monkeypatch):
    monkeypatch.setattr(service, "RECOGNITION_MODELS_DIR", tmp_path / "missing")
    response = client.post("/api/v1/recognition/exercise", json={"features": {"f1": 1.0}})
    assert response.status_code == 200
    assert response.json()["status"] == "not_available"
    assert response.json()["experimental"] is True


def test_models_endpoint_and_explicit_analyze_routes_remain_registered():
    response = client.get("/api/v1/recognition/models")
    assert response.status_code == 200
    paths = {route.path for route in app.routes}
    assert "/api/v1/analyze/squat" in paths
    assert "/api/v1/analyze/sit-to-stand" in paths

