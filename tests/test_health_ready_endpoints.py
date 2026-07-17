from fastapi.testclient import TestClient

from backend.app.main import app


client = TestClient(app)


def test_health_contract():
    response = client.get("/health")
    assert response.status_code == 200
    assert {"status", "app_version", "environment", "database_status", "artifact_dirs_status", "enabled_features"} <= response.json().keys()
    assert response.json()["artifact_dirs_status"] == "ok"


def test_ready_contract():
    response = client.get("/ready")
    assert response.status_code == 200
    assert response.json()["config_loaded"] is True
    assert response.json()["database_connection"] == "ok"
    assert response.json()["artifact_directories"] == "writable"
