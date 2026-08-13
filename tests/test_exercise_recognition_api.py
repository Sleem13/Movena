from fastapi.testclient import TestClient

from app.main import app
from app.api.routes import exercise_recognition as route
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


def test_video_recognition_endpoint_extracts_sequence_and_removes_upload(tmp_path, monkeypatch):
    saved = tmp_path / "upload.mp4"
    saved.write_bytes(b"video")
    removed = []

    async def fake_save(_video):
        return saved

    monkeypatch.setattr(route, "save_upload_file", fake_save)
    monkeypatch.setattr(route, "extract_pose_landmarks", lambda _path: [{"landmarks": {}}])
    monkeypatch.setattr(route, "extract_mediapipe_sequence_features", lambda _frames: [{"f1": 1.0}])
    monkeypatch.setattr(
        route,
        "predict_exercise_from_sequence",
        lambda sequence, model_id=None: {
            "status": "success", "suggested_exercise_id": "push_up", "confidence": 0.8,
            "model_id": "exercise_pose_gru_test", "analyzer_available": True,
            "confidence_threshold": 0.6,
        },
    )
    monkeypatch.setattr(route, "remove_file", lambda path: removed.append(path))
    response = client.post(
        "/api/v1/recognition/video",
        files={"video": ("clip.mp4", b"video", "video/mp4")},
    )
    assert response.status_code == 200
    assert response.json()["suggested_exercise_id"] == "push_up"
    assert response.json()["usable_pose_frames"] == 1
    assert response.json()["audit_status"] == "saved"
    event_id = response.json()["recognition_event_id"]
    confirmation = client.post("/api/v1/recognition/confirm", json={
        "event_id": event_id, "confirmed_exercise_id": "push_up",
    })
    assert confirmation.status_code == 200
    assert confirmation.json()["confirmed_exercise_id"] == "push_up"
    assert removed == [saved]


def test_video_recognition_accepts_subject_warning_override(tmp_path, monkeypatch):
    saved = tmp_path / "upload.mp4"
    saved.write_bytes(b"video")
    seen = {}

    async def fake_save(_video):
        return saved

    def fake_extract(_path, *, continue_on_subject_warning=False):
        seen["continue_on_subject_warning"] = continue_on_subject_warning
        return [{"landmarks": {}}]

    monkeypatch.setattr(route, "save_upload_file", fake_save)
    monkeypatch.setattr(route, "extract_pose_landmarks", fake_extract)
    monkeypatch.setattr(route, "extract_mediapipe_sequence_features", lambda _frames: [{"f1": 1.0}])
    monkeypatch.setattr(
        route,
        "predict_exercise_from_sequence",
        lambda sequence, model_id=None: {
            "status": "success",
            "suggested_exercise_id": "walking_gait_screen",
            "confidence": 0.91,
            "model_id": "exercise_pose_gru_test",
            "analyzer_available": True,
            "confidence_threshold": 0.6,
        },
    )
    monkeypatch.setattr(route, "remove_file", lambda _path: None)

    response = client.post(
        "/api/v1/recognition/video?continue_on_subject_warning=true",
        files={"video": ("clip.mp4", b"video", "video/mp4")},
    )

    assert response.status_code == 200
    assert seen["continue_on_subject_warning"] is True
    assert response.json()["suggested_exercise_id"] == "walking_gait_screen"
