from fastapi.testclient import TestClient

from app.core.config import get_settings
from app.main import app
from app.schemas.analysis_schema import AnalysisResponse, MLPrediction


client = TestClient(app)


def test_endpoint_schema_and_ml_not_applicable(monkeypatch, tmp_path):
    monkeypatch.setattr(get_settings(), "upload_dir", tmp_path)
    monkeypatch.setattr("app.api.routes.hip_abduction_analysis.extract_pose_landmarks", lambda _path: [{"landmarks": {}}])
    monkeypatch.setattr("app.api.routes.hip_abduction_analysis.hip_abduction_analyzer.analyze_landmarks", lambda _frames, include_frame_data=False: AnalysisResponse(exercise="hip_abduction", exercise_id="hip_abduction", exercise_name="Hip Abduction", total_reps=2, valid_reps=2, movement_score=85, average_hip_abduction_angle=30, ml_prediction=MLPrediction(enabled=False, model_version="not_applicable", warning="ML prediction is not applicable for hip abduction.")))
    response = client.post("/api/v1/analyze/hip-abduction?include_ml=true", files={"video": ("hip.mp4", b"video", "video/mp4")})
    assert response.status_code == 200
    body = response.json()
    assert body["exercise_id"] == "hip_abduction"
    assert body["average_hip_abduction_angle"] == 30
    prediction = body["ml_prediction"]
    assert prediction["enabled"] is False
    assert prediction["provider_status"] == "not_configured"
    assert prediction["exercise_id"] == "hip_abduction"
