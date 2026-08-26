"""Durable background analysis lifecycle and isolated worker supervision."""

from __future__ import annotations

import json
import os
import subprocess
import sys
import threading
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4

from fastapi import UploadFile
from sqlalchemy import select

from app.core.config import get_settings
from app.db.database import SessionLocal
from app.db.models import AnalysisJob, User
from app.schemas.analysis_job_schema import AnalysisJobResponse
from app.services.upload_validation_service import (
    UploadValidationError,
    validate_stream_size,
    validate_upload_metadata,
)


TERMINAL_STATUSES = {"completed", "failed", "cancelled"}
ANALYSIS_ENDPOINTS = {
    "bodyweight_squat": "squat",
    "sit_to_stand": "sit-to-stand",
    "knee_extension": "knee-extension",
    "shoulder_abduction": "shoulder-abduction",
    "shoulder_flexion": "shoulder-flexion",
    "hip_abduction": "hip-abduction",
    "push_up": "push-up",
    "shoulder_press": "shoulder-press",
    "bicep_curl": "bicep-curl",
    "hammer_curl": "hammer-curl",
    "walking_gait_screen": "gait",
    "balance": "balance",
}
_processes: dict[str, subprocess.Popen] = {}
_process_lock = threading.Lock()
_worker_slots = threading.Semaphore(max(1, int(os.getenv("ANALYSIS_JOB_MAX_CONCURRENCY", "1"))))


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


def queued_upload_dir() -> Path:
    path = get_settings().artifact_dir / "queued_uploads"
    path.mkdir(parents=True, exist_ok=True)
    return path


async def save_queued_upload(video: UploadFile, job_id: str) -> Path:
    validate_upload_metadata(video)
    settings = get_settings()
    suffix = Path(video.filename or "video.mp4").suffix.lower()
    destination = queued_upload_dir() / f"{job_id}{suffix}"
    total_bytes = 0
    with destination.open("wb") as buffer:
        while chunk := await video.read(1024 * 1024):
            total_bytes += len(chunk)
            if total_bytes > settings.max_upload_size_bytes:
                destination.unlink(missing_ok=True)
                raise UploadValidationError("FILE_TOO_LARGE", "Uploaded file exceeds the maximum allowed size.")
            buffer.write(chunk)
    try:
        validate_stream_size(total_bytes, settings)
    except UploadValidationError:
        destination.unlink(missing_ok=True)
        raise
    return destination


def create_analysis_job(
    *,
    user: User,
    exercise_id: str,
    source_path: Path,
    source_filename: str,
    content_type: str | None,
    options: dict,
    job_id: str | None = None,
) -> AnalysisJob:
    row = AnalysisJob(
        job_id=job_id or str(uuid4()),
        owner_user_id=user.user_id,
        exercise_id=exercise_id,
        status="queued",
        stage="queued",
        progress=5,
        source_path=str(source_path),
        source_filename=source_filename,
        content_type=content_type,
        options_json=json.dumps(options),
        max_attempts=2,
    )
    with SessionLocal() as db:
        db.add(row)
        db.commit()
        db.refresh(row)
        return row


def analysis_job_response(row: AnalysisJob) -> AnalysisJobResponse:
    result = None
    if row.result_json:
        try:
            result = json.loads(row.result_json)
        except json.JSONDecodeError:
            result = None
    return AnalysisJobResponse(
        job_id=row.job_id,
        exercise_id=row.exercise_id,
        status=row.status,
        stage=row.stage,
        progress=row.progress,
        attempts=row.attempts,
        max_attempts=row.max_attempts,
        cancel_requested=row.cancel_requested,
        error_code=row.error_code,
        message=row.message,
        http_status=row.http_status,
        result=result,
        created_at=row.created_at,
        started_at=row.started_at,
        completed_at=row.completed_at,
    )


def get_owned_job(job_id: str, user: User) -> AnalysisJob | None:
    with SessionLocal() as db:
        row = db.scalar(select(AnalysisJob).where(AnalysisJob.job_id == job_id))
        if row is None:
            return None
        if row.owner_user_id != user.user_id and user.role != "super_admin":
            return None
        db.expunge(row)
        return row


def _mark_worker_exit(job_id: str, return_code: int) -> tuple[bool, int]:
    """Return whether the job should retry and the current attempt count."""
    with SessionLocal() as db:
        row = db.scalar(select(AnalysisJob).where(AnalysisJob.job_id == job_id))
        if row is None:
            return False, 0
        if row.cancel_requested or row.status == "cancelled":
            row.status = "cancelled"
            row.stage = "cancelled"
            row.progress = 0
            row.completed_at = utc_now()
            db.commit()
            return False, row.attempts
        if row.status == "completed":
            return False, row.attempts
        if row.status == "failed" and return_code == 0:
            return False, row.attempts
        if return_code != 0 and not row.error_code:
            row.error_code = "WORKER_EXITED"
            row.message = "The background analysis worker stopped unexpectedly."
        should_retry = row.attempts < row.max_attempts
        if should_retry:
            row.status = "queued"
            row.stage = "retrying"
            row.progress = 10
        else:
            row.status = "failed"
            row.stage = "failed"
            row.progress = 100
            row.completed_at = utc_now()
        db.commit()
        return should_retry, row.attempts


def run_analysis_job(job_id: str) -> None:
    """Supervise an isolated worker, retrying one unexpected failure."""
    with _worker_slots:
        while True:
            with SessionLocal() as db:
                row = db.scalar(select(AnalysisJob).where(AnalysisJob.job_id == job_id))
                if row is None or row.status in TERMINAL_STATUSES or row.cancel_requested:
                    return
                row.attempts += 1
                row.stage = "starting"
                row.progress = max(row.progress, 10)
                db.commit()

            environment = os.environ.copy()
            environment["ANALYSIS_JOB_WORKER"] = "1"
            process = subprocess.Popen(
                [sys.executable, "-m", "app.workers.analysis_job_worker", job_id],
                cwd=Path(__file__).resolve().parents[2],
                env=environment,
            )
            with _process_lock:
                _processes[job_id] = process
            return_code = process.wait()
            with _process_lock:
                _processes.pop(job_id, None)
            should_retry, _attempt = _mark_worker_exit(job_id, return_code)
            if not should_retry:
                break

    with SessionLocal() as db:
        row = db.scalar(select(AnalysisJob).where(AnalysisJob.job_id == job_id))
        if row and row.status in TERMINAL_STATUSES:
            Path(row.source_path).unlink(missing_ok=True)


def launch_analysis_job(job_id: str) -> None:
    thread = threading.Thread(target=run_analysis_job, args=(job_id,), daemon=True, name=f"analysis-job-{job_id[:8]}")
    thread.start()


def cancel_analysis_job(job_id: str, user: User) -> AnalysisJob | None:
    with SessionLocal() as db:
        row = db.scalar(select(AnalysisJob).where(AnalysisJob.job_id == job_id))
        if row is None or (row.owner_user_id != user.user_id and user.role != "super_admin"):
            return None
        if row.status not in TERMINAL_STATUSES:
            row.cancel_requested = True
            row.status = "cancelled"
            row.stage = "cancelled"
            row.progress = 0
            row.completed_at = utc_now()
            source_path = Path(row.source_path)
            db.commit()
        else:
            source_path = Path(row.source_path)
        db.refresh(row)
        db.expunge(row)

    with _process_lock:
        process = _processes.get(job_id)
    if process and process.poll() is None:
        process.terminate()
        try:
            process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            process.kill()
    source_path.unlink(missing_ok=True)
    return row


def recover_analysis_jobs() -> int:
    """Resume queued/running work after an API task restart."""
    with SessionLocal() as db:
        rows = list(db.scalars(select(AnalysisJob).where(AnalysisJob.status.in_(["queued", "running"]))))
        recoverable = []
        for row in rows:
            if row.cancel_requested or not Path(row.source_path).is_file():
                row.status = "cancelled" if row.cancel_requested else "failed"
                row.stage = row.status
                row.progress = 0 if row.cancel_requested else 100
                row.error_code = None if row.cancel_requested else "SOURCE_UNAVAILABLE"
                row.message = None if row.cancel_requested else "The queued video is no longer available."
                row.completed_at = utc_now()
            else:
                row.status = "queued"
                row.stage = "recovered"
                row.progress = max(5, min(row.progress, 15))
                recoverable.append(row.job_id)
        db.commit()
    for job_id in recoverable:
        launch_analysis_job(job_id)
    return len(recoverable)
