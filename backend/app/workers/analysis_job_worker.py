"""Execute one analysis job in a cancellable process."""

from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlencode

from fastapi.testclient import TestClient
from sqlalchemy import select

from app.core.security import create_access_token
from app.db.database import SessionLocal
from app.db.models import AnalysisJob, User
from app.services.analysis_job_service import ANALYSIS_ENDPOINTS


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


def update_job(job_id: str, **values) -> AnalysisJob | None:
    with SessionLocal() as db:
        row = db.scalar(select(AnalysisJob).where(AnalysisJob.job_id == job_id))
        if row is None:
            return None
        if row.cancel_requested or row.status == "cancelled":
            return row
        for key, value in values.items():
            setattr(row, key, value)
        db.commit()
        db.refresh(row)
        return row


def execute(job_id: str) -> int:
    with SessionLocal() as db:
        job = db.scalar(select(AnalysisJob).where(AnalysisJob.job_id == job_id))
        if job is None or job.cancel_requested or job.status == "cancelled":
            return 0
        user = db.scalar(select(User).where(User.user_id == job.owner_user_id))
        if user is None:
            job.status = "failed"
            job.stage = "failed"
            job.progress = 100
            job.error_code = "OWNER_UNAVAILABLE"
            job.message = "The account that started this analysis is unavailable."
            job.completed_at = utc_now()
            db.commit()
            return 0
        source_path = Path(job.source_path)
        source_filename = job.source_filename
        content_type = job.content_type or "application/octet-stream"
        exercise_id = job.exercise_id
        options = json.loads(job.options_json or "{}")
        token = create_access_token(user.user_id, user.role, token_version=user.token_version)

    endpoint = ANALYSIS_ENDPOINTS.get(exercise_id)
    if endpoint is None or not source_path.is_file():
        update_job(
            job_id,
            status="failed",
            stage="failed",
            progress=100,
            error_code="UNSUPPORTED_EXERCISE" if endpoint is None else "SOURCE_UNAVAILABLE",
            message="The selected exercise is not supported." if endpoint is None else "The queued video is no longer available.",
            completed_at=utc_now(),
        )
        return 0

    update_job(job_id, status="running", stage="analyzing", progress=30, started_at=utc_now())
    query = urlencode({key: str(bool(value)).lower() if isinstance(value, bool) else value for key, value in options.items() if value is not None})

    from app.main import app

    try:
        with source_path.open("rb") as video_stream, TestClient(app) as client:
            response = client.post(
                f"/api/v1/analyze/{endpoint}?{query}",
                files={"video": (source_filename, video_stream, content_type)},
                headers={"Authorization": f"Bearer {token}"},
            )
        try:
            payload = response.json()
        except ValueError:
            payload = {"error_code": "INVALID_WORKER_RESPONSE", "message": "The analysis worker returned an invalid response."}
    except Exception as exc:
        update_job(
            job_id,
            stage="retrying",
            progress=60,
            error_code="WORKER_REQUEST_FAILED",
            message=str(exc),
            http_status=500,
        )
        return 2

    with SessionLocal() as db:
        row = db.scalar(select(AnalysisJob).where(AnalysisJob.job_id == job_id))
        if row is None or row.cancel_requested or row.status == "cancelled":
            return 0
        if response.status_code < 400:
            row.status = "completed"
            row.stage = "completed"
            row.progress = 100
            row.result_json = json.dumps(payload)
            row.error_code = None
            row.message = None
            row.http_status = response.status_code
            row.completed_at = utc_now()
            db.commit()
            source_path.unlink(missing_ok=True)
            return 0
        row.error_code = payload.get("error_code", "ANALYSIS_FAILED")
        row.message = payload.get("message", "The analysis could not be completed.")
        row.http_status = response.status_code
        if response.status_code >= 500:
            row.stage = "retrying"
            row.progress = 70
            db.commit()
            return 2
        row.status = "failed"
        row.stage = "failed"
        row.progress = 100
        row.result_json = json.dumps(payload)
        row.completed_at = utc_now()
        db.commit()
        source_path.unlink(missing_ok=True)
        return 0


if __name__ == "__main__":
    raise SystemExit(execute(sys.argv[1]) if len(sys.argv) == 2 else 64)
