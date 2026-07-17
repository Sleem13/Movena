from fastapi.testclient import TestClient

from app.core.config import get_settings
from app.main import app
from app.schemas.analysis_schema import AnalysisResponse, MLPrediction


client = TestClient(app)


def test_endpoint_schema_and_ml_not_applicable(monkeypatch, tmp_path):
    monkeypatch.setattr(get_settings(), "upload_dir", tmp_path)
    monkeypatch.setattr("app.api.routes.shoulder_abduction_analysis.extract_pose_landmarks", lambda _path: [{"landmarks": {}}])
    monkeypatch.setattr("app.api.routes.shoulder_abduction_analysis.shoulder_abduction_analyzer.analyze_landmarks", lambda _frames, include_frame_data=False: AnalysisResponse(exercise="shoulder_abduction", exercise_id="shoulder_abduction", exercise_name="Shoulder Abduction", total_reps=2, valid_reps=2, movement_score=85, average_shoulder_angle=88, ml_prediction=MLPrediction(enabled=False, model_version="not_applicable", warning="ML prediction is not applicable for shoulder abduction.")))
    response = client.post("/api/v1/analyze/shoulder-abduction?include_ml=true", files={"video": ("arm.mp4", b"video", "video/mp4")})
    assert response.status_code == 200
    body = response.json()
    assert body["exercise_id"] == "shoulder_abduction"
    assert body["average_shoulder_angle"] == 88
    assert body["ml_prediction"]["enabled"] is False
