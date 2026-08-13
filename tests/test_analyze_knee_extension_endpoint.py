from fastapi.testclient import TestClient

from app.core.config import get_settings
from app.main import app
from app.schemas.analysis_schema import AnalysisResponse, MLPrediction


client = TestClient(app)


def test_endpoint_returns_rule_result_and_ml_not_applicable(monkeypatch, tmp_path):
    monkeypatch.setattr(get_settings(), "upload_dir", tmp_path)
    monkeypatch.setattr("app.api.routes.knee_extension_analysis.extract_pose_landmarks", lambda _path: [{"landmarks": {}}])
    monkeypatch.setattr(
        "app.api.routes.knee_extension_analysis.knee_extension_analyzer.analyze_landmarks",
        lambda _frames, include_frame_data=False: AnalysisResponse(
            exercise="knee_extension", exercise_id="knee_extension", exercise_name="Knee Extension",
            total_reps=2, valid_reps=2, movement_score=86,
            ml_prediction=MLPrediction(enabled=False, model_version="not_applicable", warning="ML prediction is not applicable for knee extension."),
        ),
    )
    response = client.post("/api/v1/analyze/knee-extension?include_ml=true", files={"video": ("extension.mp4", b"video", "video/mp4")})
    assert response.status_code == 200
    body = response.json()
    assert body["exercise_id"] == "knee_extension"
    assert body["valid_reps"] == 2
    prediction = body["ml_prediction"]
    assert prediction["enabled"] is False
    assert prediction["model_version"] == "not_configured"
    assert prediction["provider_status"] == "not_configured"
    assert "pretrained/fine-tuned/feature-extractor provider" in prediction["warning"]
