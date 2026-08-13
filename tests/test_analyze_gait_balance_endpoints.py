from fastapi.testclient import TestClient

from app.core.config import get_settings
from app.main import app
from app.schemas.analysis_schema import AnalysisResponse, MLPrediction


client = TestClient(app)


def _rule_response(exercise_id: str, display_name: str) -> AnalysisResponse:
    return AnalysisResponse(
        exercise=exercise_id,
        exercise_id=exercise_id,
        exercise_name=display_name,
        status="success",
        movement_score=80,
        ml_prediction=MLPrediction(
            enabled=False,
            model_version="not_applicable",
            warning="Rule-based analyzer remains primary.",
        ),
    )


def test_gait_endpoint_accepts_ml_second_opinion_request(monkeypatch, tmp_path):
    monkeypatch.setattr(get_settings(), "upload_dir", tmp_path)
    monkeypatch.setattr("app.api.routes.gait_analysis.extract_pose_landmarks", lambda _path: [{"landmarks": {}}])
    monkeypatch.setattr(
        "app.api.routes.gait_analysis.gait_analyzer.analyze_landmarks",
        lambda _frames, include_frame_data=False: _rule_response("walking_gait_screen", "Walking Gait Screen"),
    )

    response = client.post("/api/v1/analyze/gait?include_ml=true", files={"video": ("gait.mp4", b"video", "video/mp4")})

    assert response.status_code == 200
    prediction = response.json()["ml_prediction"]
    assert prediction["exercise_id"] == "walking_gait_screen"
    assert prediction["provider_status"] == "not_configured"
    assert "feature_extractor" in prediction["supported_model_modes"]


def test_balance_endpoint_accepts_ml_second_opinion_request(monkeypatch, tmp_path):
    monkeypatch.setattr(get_settings(), "upload_dir", tmp_path)
    monkeypatch.setattr("app.api.routes.balance_analysis.extract_pose_landmarks", lambda _path: [{"landmarks": {}}])
    monkeypatch.setattr(
        "app.api.routes.balance_analysis.balance_analyzer.analyze_landmarks",
        lambda _frames, include_frame_data=False: _rule_response("balance", "Static Balance Screen"),
    )

    response = client.post("/api/v1/analyze/balance?include_ml=true", files={"video": ("balance.mp4", b"video", "video/mp4")})

    assert response.status_code == 200
    prediction = response.json()["ml_prediction"]
    assert prediction["exercise_id"] == "balance"
    assert prediction["provider_status"] == "not_configured"
    assert "pretrained_as_is" in prediction["supported_model_modes"]
