from fastapi.testclient import TestClient

from app.core.config import get_settings
from app.main import app
from app.services.ml_prediction_service import INVALID_SQUAT_WARNING
from app.services.squat_analysis_service import analyze_squat_landmarks
from app.tests.test_squat_analysis import frame, squat_sequence


client = TestClient(app)


def static_frames(count=45):
    frames = [frame(knee_angle=170) for _ in range(count)]
    for index, item in enumerate(frames):
        item.update(
            frame_index=index,
            timestamp_sec=index / 30,
            source_total_frames=count,
        )
    return frames


def test_zero_rep_static_video_is_rejected_without_movement_score():
    report = analyze_squat_landmarks(static_frames())
    assert report.status == "rejected"
    assert report.error_code == "INVALID_SQUAT_VIDEO"
    assert report.total_reps == 0
    assert report.movement_score is None
    assert report.detected_issues == ["no_valid_squat_detected"]
    assert "poor_depth" not in report.detected_issues
    assert report.input_validity.is_valid is False
    assert report.analysis_confidence.level == "low"


def test_valid_squat_still_returns_success_and_score():
    report = analyze_squat_landmarks(squat_sequence())
    assert report.status == "success"
    assert report.total_reps == 1
    assert report.movement_score is not None
    assert report.input_validity.is_valid is True


def test_ml_is_skipped_for_invalid_video(monkeypatch, tmp_path):
    monkeypatch.setattr(get_settings(), "upload_dir", tmp_path)
    monkeypatch.setattr(
        "app.api.routes.squat_analysis.extract_pose_landmarks",
        lambda _path: static_frames(),
    )

    def should_not_run(_frames):
        raise AssertionError("ML inference must not run for rejected input")

    monkeypatch.setattr(
        "app.services.ml_second_opinion_service.predict_experimental_quality", should_not_run
    )
    response = client.post(
        "/api/v1/analyze/squat?include_ml=true",
        files={"video": ("static.mp4", b"video", "video/mp4")},
    )
    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "rejected"
    assert payload["movement_score"] is None
    assert payload["ml_prediction"]["enabled"] is False
    assert payload["ml_prediction"]["warning"] == INVALID_SQUAT_WARNING
