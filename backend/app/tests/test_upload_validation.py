from pathlib import Path

from fastapi.testclient import TestClient

from app.core.config import get_settings
from app.main import app
from app.schemas.analysis_schema import AnalysisResponse
from app.services.pose_estimation_service import PoseEstimationError


client = TestClient(app)


def assert_error(response, status_code: int, error_code: str) -> None:
    assert response.status_code == status_code
    assert response.json()["status"] == "error"
    assert response.json()["error_code"] == error_code
    assert isinstance(response.json()["details"], list)


def test_missing_video_returns_clean_error():
    assert_error(client.post("/api/v1/analyze/squat"), 422, "MISSING_FILE")


def test_non_video_validation_error_is_not_reported_as_missing_video():
    response = client.post(
        "/api/v1/auth/register",
        json={
            "email": "reviewer@example.com",
            "password": "too-short",
            "full_name": "Reviewer",
            "role": "researcher_demo",
        },
    )

    assert_error(response, 422, "VALIDATION_ERROR")
    assert response.json()["message"] == "Password must be at least 12 characters."
    assert "video" not in response.json()["message"].lower()


def test_unsupported_extension_returns_clean_error():
    response = client.post(
        "/api/v1/analyze/squat",
        files={"video": ("notes.txt", b"not video", "text/plain")},
    )
    assert_error(response, 400, "UNSUPPORTED_FILE_TYPE")


def test_mismatched_mime_type_returns_clean_error():
    response = client.post(
        "/api/v1/analyze/squat",
        files={"video": ("clip.mp4", b"not video", "text/plain")},
    )
    assert_error(response, 400, "UNSUPPORTED_FILE_TYPE")


def test_empty_video_returns_clean_error():
    response = client.post(
        "/api/v1/analyze/squat",
        files={"video": ("empty.mp4", b"", "video/mp4")},
    )
    assert_error(response, 400, "EMPTY_FILE")


def test_file_size_limit_is_enforced(monkeypatch, tmp_path):
    settings = get_settings()
    monkeypatch.setattr(settings, "upload_dir", tmp_path)
    monkeypatch.setattr(settings, "max_upload_size_bytes", 4)

    response = client.post(
        "/api/v1/analyze/squat",
        files={"video": ("large.mp4", b"12345", "video/mp4")},
    )

    assert_error(response, 400, "FILE_TOO_LARGE")
    assert list(tmp_path.iterdir()) == []


def test_broken_video_returns_clean_error_and_is_deleted(monkeypatch, tmp_path):
    settings = get_settings()
    monkeypatch.setattr(settings, "upload_dir", tmp_path)

    def fail_pose(_path: Path):
        raise PoseEstimationError("Unable to open uploaded video.")

    monkeypatch.setattr("app.api.routes.squat_analysis.extract_pose_landmarks", fail_pose)
    response = client.post(
        "/api/v1/analyze/squat",
        files={"video": ("broken.mp4", b"broken", "video/mp4")},
    )

    assert_error(response, 422, "VIDEO_OPEN_FAILED")
    assert list(tmp_path.iterdir()) == []


def test_no_pose_returns_clean_error(monkeypatch, tmp_path):
    monkeypatch.setattr(get_settings(), "upload_dir", tmp_path)

    def fail_pose(_path: Path):
        raise PoseEstimationError("No pose detected in the uploaded video.")

    monkeypatch.setattr("app.api.routes.squat_analysis.extract_pose_landmarks", fail_pose)
    response = client.post(
        "/api/v1/analyze/squat",
        files={"video": ("no-pose.mp4", b"video", "video/mp4")},
    )
    assert_error(response, 422, "NO_POSE_DETECTED")


def test_subject_switch_returns_structured_rejection(monkeypatch, tmp_path):
    monkeypatch.setattr(get_settings(), "upload_dir", tmp_path)

    def fail_pose(_path: Path):
        raise PoseEstimationError(
            "The tracked pose appears to switch between people.",
            error_code="SUBJECT_SWITCH_DETECTED",
            details=["Possible subject switch near 12.87s.", "Record only one person."],
        )

    monkeypatch.setattr("app.api.routes.squat_analysis.extract_pose_landmarks", fail_pose)
    response = client.post(
        "/api/v1/analyze/squat",
        files={"video": ("two-people.mp4", b"video", "video/mp4")},
    )

    assert_error(response, 422, "SUBJECT_SWITCH_DETECTED")
    assert response.json()["details"] == [
        "Possible subject switch near 12.87s.",
        "Record only one person.",
    ]


def test_subject_switch_warning_can_be_overridden_with_report_warning(monkeypatch, tmp_path):
    monkeypatch.setattr(get_settings(), "upload_dir", tmp_path)

    def extract_with_warning(_path: Path, *, continue_on_subject_warning: bool = False):
        assert continue_on_subject_warning is True
        return [{"landmarks": {}, "subject_continuity_warning": "Subject-continuity warning overridden by user request. Possible subject switch near 12.87s."}]

    monkeypatch.setattr("app.api.routes.squat_analysis.extract_pose_landmarks", extract_with_warning)
    monkeypatch.setattr(
        "app.api.routes.squat_analysis.analyze_squat_landmarks",
        lambda _frames, include_frame_data=False: AnalysisResponse(
            total_reps=1,
            movement_score=80,
            feedback=["Educational only."],
            limitations=["Does not replace clinical assessment."],
        ),
    )

    response = client.post(
        "/api/v1/analyze/squat?continue_on_subject_warning=true",
        files={"video": ("two-people.mp4", b"video", "video/mp4")},
    )

    assert response.status_code == 200
    body = response.json()
    assert any("Subject-continuity warning overridden" in warning for warning in body["validation_warnings"])
    assert any("manually review" in limitation for limitation in body["limitations"])


def test_success_response_contract_and_cleanup(monkeypatch, tmp_path):
    monkeypatch.setattr(get_settings(), "upload_dir", tmp_path)
    artifact_dir = tmp_path / "artifacts"
    monkeypatch.setattr(get_settings(), "artifact_dir", artifact_dir)
    monkeypatch.setattr(
        "app.api.routes.squat_analysis.extract_pose_landmarks",
        lambda _path: [{"landmarks": {}}],
    )
    monkeypatch.setattr(
        "app.api.routes.squat_analysis.analyze_squat_landmarks",
        lambda _frames, include_frame_data=False: AnalysisResponse(
            total_reps=1,
            movement_score=90,
            feedback=["Educational only."],
            limitations=["Does not replace clinical assessment."],
        ),
    )

    response = client.post(
        "/api/v1/analyze/squat?generate_report=true",
        files={"video": ("valid.mp4", b"video", "video/mp4")},
    )

    assert response.status_code == 200
    assert response.json()["exercise"] == "bodyweight_squat"
    assert response.json()["total_reps"] == 1
    assert response.json()["report_download_url"].startswith("/api/v1/artifacts/reports/")
    assert not list(tmp_path.glob("*.mp4"))


def test_processing_failure_has_clean_message_without_stack_trace(monkeypatch, tmp_path):
    monkeypatch.setattr(get_settings(), "upload_dir", tmp_path)
    monkeypatch.setattr(
        "app.api.routes.squat_analysis.extract_pose_landmarks",
        lambda _path: [{"landmarks": {}}],
    )

    def fail_analysis(_frames, include_frame_data=False):
        raise RuntimeError("sensitive internal path C:/private")

    monkeypatch.setattr("app.api.routes.squat_analysis.analyze_squat_landmarks", fail_analysis)
    response = client.post(
        "/api/v1/analyze/squat",
        files={"video": ("valid.mp4", b"video", "video/mp4")},
    )
    assert_error(response, 500, "PROCESSING_ERROR")
    assert "private" not in response.text
