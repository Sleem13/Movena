from pathlib import Path
from types import SimpleNamespace

from fastapi.testclient import TestClient

from app.api.dependencies.auth import get_current_user
from app.api.routes import analysis_jobs as routes
from app.core.config import get_settings
from app.core.security import get_password_hash
from app.db.database import SessionLocal
from app.db.models import AnalysisJob, User
from app.main import app
from app.services.analysis_job_service import create_analysis_job
from app.workers.analysis_job_worker import execute


def test_analysis_job_can_be_created_polled_and_cancelled(monkeypatch, tmp_path: Path):
    user = SimpleNamespace(user_id="job-owner", role="therapist")
    app.dependency_overrides[get_current_user] = lambda: user
    monkeypatch.setattr(routes, "launch_analysis_job", lambda _job_id: None)
    monkeypatch.setattr(get_settings(), "artifact_dir", tmp_path)
    try:
        with TestClient(app) as client:
            created = client.post(
                "/api/v1/analysis-jobs/push_up?include_overlay=true&generate_report=true",
                files={"video": ("movement.mp4", b"safe-test-video", "video/mp4")},
            )
            assert created.status_code == 202
            job = created.json()
            assert job["exercise_id"] == "push_up"
            assert job["status"] == "queued"
            assert job["progress"] == 5

            polled = client.get(f"/api/v1/analysis-jobs/{job['job_id']}")
            assert polled.status_code == 200
            assert polled.json()["job_id"] == job["job_id"]

            cancelled = client.post(f"/api/v1/analysis-jobs/{job['job_id']}/cancel")
            assert cancelled.status_code == 200
            assert cancelled.json()["status"] == "cancelled"
            assert not list((tmp_path / "queued_uploads").glob("*"))
    finally:
        app.dependency_overrides.clear()


def test_analysis_job_rejects_unsupported_exercise(monkeypatch, tmp_path: Path):
    app.dependency_overrides[get_current_user] = lambda: SimpleNamespace(user_id="job-owner", role="therapist")
    monkeypatch.setattr(get_settings(), "artifact_dir", tmp_path)
    try:
        response = TestClient(app).post(
            "/api/v1/analysis-jobs/not-real",
            files={"video": ("movement.mp4", b"safe-test-video", "video/mp4")},
        )
        assert response.status_code == 404
        assert response.json()["error_code"] == "UNSUPPORTED_EXERCISE"
    finally:
        app.dependency_overrides.clear()


def test_analysis_job_is_private_to_its_owner(monkeypatch, tmp_path: Path):
    active_user = {"value": SimpleNamespace(user_id="owner-a", role="therapist")}
    app.dependency_overrides[get_current_user] = lambda: active_user["value"]
    monkeypatch.setattr(routes, "launch_analysis_job", lambda _job_id: None)
    monkeypatch.setattr(get_settings(), "artifact_dir", tmp_path)
    try:
        with TestClient(app) as client:
            created = client.post(
                "/api/v1/analysis-jobs/push_up",
                files={"video": ("movement.mp4", b"safe-test-video", "video/mp4")},
            ).json()
            active_user["value"] = SimpleNamespace(user_id="owner-b", role="therapist")
            hidden = client.get(f"/api/v1/analysis-jobs/{created['job_id']}")
            assert hidden.status_code == 404
    finally:
        app.dependency_overrides.clear()


def test_worker_records_a_deterministic_analysis_failure(monkeypatch, tmp_path: Path):
    monkeypatch.setenv("ANALYSIS_JOB_WORKER", "1")
    source = tmp_path / "invalid.mp4"
    source.write_bytes(b"not-a-valid-video")
    user = User(
        user_id="worker-owner",
        username="worker.owner",
        email="worker@example.com",
        password_hash=get_password_hash("StrongPassword123"),
        full_name="Worker Owner",
        role="therapist",
        is_active=True,
        is_verified=True,
    )
    with SessionLocal() as db:
        db.add(user)
        db.commit()
    job = create_analysis_job(
        user=user,
        exercise_id="push_up",
        source_path=source,
        source_filename="invalid.mp4",
        content_type="video/mp4",
        options={"include_overlay": False, "generate_report": False},
    )
    assert execute(job.job_id) == 0
    with SessionLocal() as db:
        completed = db.query(AnalysisJob).filter_by(job_id=job.job_id).one()
        assert completed.status == "failed"
        assert completed.http_status in {400, 422}
        assert completed.error_code
    assert not source.exists()
