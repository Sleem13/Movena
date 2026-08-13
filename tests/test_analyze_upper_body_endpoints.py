from fastapi.testclient import TestClient

from app.core.config import get_settings
from app.main import app
from app.schemas.analysis_schema import AnalysisResponse, MLPrediction


client = TestClient(app)


def _response(exercise_id, display_name):
    return AnalysisResponse(exercise=exercise_id, exercise_id=exercise_id, exercise_name=display_name, total_reps=2, valid_reps=2, movement_score=82, average_elbow_angle=140, ml_prediction=MLPrediction(enabled=False, model_version="not_applicable", warning="Rule-based analyzer remains primary."))


def test_push_up_endpoint_uses_dedicated_analyzer(monkeypatch, tmp_path):
    monkeypatch.setattr(get_settings(), "upload_dir", tmp_path)
    monkeypatch.setattr("app.api.routes.upper_body_analysis.extract_pose_landmarks", lambda _path: [{"landmarks": {}}])
    monkeypatch.setattr("app.api.routes.upper_body_analysis.push_up_analyzer.analyze_landmarks", lambda _frames, include_frame_data=False: _response("push_up", "Push-Up"))
    response = client.post("/api/v1/analyze/push-up", files={"video": ("push-up.mp4", b"video", "video/mp4")})
    assert response.status_code == 200
    assert response.json()["exercise_id"] == "push_up"
    assert response.json()["average_elbow_angle"] == 140


def test_shoulder_press_endpoint_uses_dedicated_analyzer(monkeypatch, tmp_path):
    monkeypatch.setattr(get_settings(), "upload_dir", tmp_path)
    monkeypatch.setattr("app.api.routes.upper_body_analysis.extract_pose_landmarks", lambda _path: [{"landmarks": {}}])
    monkeypatch.setattr("app.api.routes.upper_body_analysis.shoulder_press_analyzer.analyze_landmarks", lambda _frames, include_frame_data=False: _response("shoulder_press", "Shoulder Press"))
    response = client.post("/api/v1/analyze/shoulder-press", files={"video": ("press.mp4", b"video", "video/mp4")})
    assert response.status_code == 200
    assert response.json()["exercise_id"] == "shoulder_press"


def test_bicep_curl_endpoint_uses_dedicated_analyzer(monkeypatch, tmp_path):
    monkeypatch.setattr(get_settings(), "upload_dir", tmp_path)
    monkeypatch.setattr("app.api.routes.upper_body_analysis.extract_pose_landmarks", lambda _path: [{"landmarks": {}}])
    monkeypatch.setattr("app.api.routes.upper_body_analysis.bicep_curl_analyzer.analyze_landmarks", lambda _frames, include_frame_data=False: _response("bicep_curl", "Bicep Curl"))
    response = client.post("/api/v1/analyze/bicep-curl", files={"video": ("curl.mp4", b"video", "video/mp4")})
    assert response.status_code == 200
    assert response.json()["exercise_id"] == "bicep_curl"


def test_hammer_curl_endpoint_uses_dedicated_analyzer(monkeypatch, tmp_path):
    monkeypatch.setattr(get_settings(), "upload_dir", tmp_path)
    monkeypatch.setattr("app.api.routes.upper_body_analysis.extract_pose_landmarks", lambda _path: [{"landmarks": {}}])
    monkeypatch.setattr("app.api.routes.upper_body_analysis.hammer_curl_analyzer.analyze_landmarks", lambda _frames, include_frame_data=False: _response("hammer_curl", "Hammer Curl"))
    response = client.post("/api/v1/analyze/hammer-curl", files={"video": ("hammer.mp4", b"video", "video/mp4")})
    assert response.status_code == 200
    assert response.json()["exercise_id"] == "hammer_curl"


def test_shoulder_flexion_endpoint_uses_dedicated_analyzer(monkeypatch, tmp_path):
    monkeypatch.setattr(get_settings(), "upload_dir", tmp_path)
    monkeypatch.setattr("app.api.routes.upper_body_analysis.extract_pose_landmarks", lambda _path: [{"landmarks": {}}])
    monkeypatch.setattr("app.api.routes.upper_body_analysis.shoulder_flexion_analyzer.analyze_landmarks", lambda _frames, include_frame_data=False: AnalysisResponse(exercise="shoulder_flexion", exercise_id="shoulder_flexion", exercise_name="Shoulder Flexion", total_reps=2, valid_reps=2, movement_score=82, average_shoulder_angle=130, ml_prediction=MLPrediction(enabled=False, model_version="not_applicable", warning="Rule-based analyzer remains primary.")))
    response = client.post("/api/v1/analyze/shoulder-flexion", files={"video": ("flexion.mp4", b"video", "video/mp4")})
    assert response.status_code == 200
    assert response.json()["exercise_id"] == "shoulder_flexion"
    assert response.json()["average_shoulder_angle"] == 130
