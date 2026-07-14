import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "backend"))

from fastapi.testclient import TestClient

from app.core.config import get_settings
from app.main import app
from app.schemas.analysis_schema import AnalysisResponse, MLPrediction


client = TestClient(app)


def test_endpoint_returns_rule_result_and_ml_unavailable(monkeypatch, tmp_path):
    monkeypatch.setattr(get_settings(), "upload_dir", tmp_path)
    monkeypatch.setattr(
        "app.api.routes.sit_to_stand_analysis.extract_pose_landmarks",
        lambda _path: [{"landmarks": {}}],
    )
    monkeypatch.setattr(
        "app.api.routes.sit_to_stand_analysis.sit_to_stand_analyzer.analyze_landmarks",
        lambda _frames, include_frame_data=False: AnalysisResponse(
            exercise="sit_to_stand", total_reps=3, movement_score=88,
            ml_prediction=MLPrediction(
                enabled=False, model_version="not_applicable",
                warning="ML prediction is not available for sit-to-stand yet.",
            ),
        ),
    )

    response = client.post(
        "/api/v1/analyze/sit-to-stand?include_ml=true",
        files={"video": ("chair.mp4", b"video", "video/mp4")},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["exercise"] == "sit_to_stand"
    assert body["total_reps"] == 3
    assert body["ml_prediction"]["enabled"] is False
    assert "not available" in body["ml_prediction"]["warning"]
