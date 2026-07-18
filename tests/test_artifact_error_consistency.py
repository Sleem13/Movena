from uuid import uuid4

import pytest
from fastapi.testclient import TestClient

from app.main import app


@pytest.mark.parametrize(
    "path",
    [
        "/api/v1/artifacts/reports/{artifact_id}",
        "/api/v1/artifacts/overlays/{artifact_id}/preview",
        "/api/v1/artifacts/overlays/{artifact_id}/download",
    ],
)
def test_missing_artifacts_return_standardized_private_404(path):
    response = TestClient(app).get(path.format(artifact_id=uuid4().hex))
    body = response.json()

    assert response.status_code == 404
    assert body["status"] == "error"
    assert body["error_code"] == "ARTIFACT_NOT_FOUND"
    assert body["details"] == []
    assert "not found or expired" in body["message"].lower()
    assert "backend" not in response.text.lower()
    assert "\\" not in response.text
