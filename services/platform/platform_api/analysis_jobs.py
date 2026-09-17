import re

from django.db import transaction

from .models import AnalysisJobRecord

PATH = re.compile(r"analysis-jobs/([^/]+)(?:/cancel)?$")
VALID = {"queued", "running", "completed", "failed", "cancelled", "rejected", "error"}


def active_for(owner_id, limit=20):
    rows = AnalysisJobRecord.objects.filter(
        owner_id=owner_id, status__in=["queued", "running"]
    ).order_by("-last_synced_at")[:limit]
    return [
        {
            "job_id": row.job_id,
            "exercise_id": row.exercise_id,
            "status": row.status,
            "stage": row.stage,
            "progress": row.progress,
            "attempts": row.attempts,
            "max_attempts": row.max_attempts,
            "cancel_requested": row.cancel_requested,
            "error_code": row.error_code,
            "message": row.message,
            "http_status": row.http_status,
            "result": row.result,
            "engine_version": row.engine_version,
            "model_version": row.model_version,
            "created_at": row.created_at,
            "started_at": row.started_at,
            "completed_at": row.completed_at,
        }
        for row in rows
    ]


def owned_or_absent(job_id, principal):
    row = AnalysisJobRecord.objects.filter(pk=job_id).only("owner_id").first()
    return row is None or row.owner_id == principal.user_id or principal.role == "super_admin"


def _outcome(data, status):
    result = data.get("result") if isinstance(data.get("result"), dict) else None
    result_status = result.get("status") if result else None
    if result_status in {"success", "rejected", "error"}:
        return result_status
    if status == "failed":
        return "error"
    return status if status in {"rejected", "error"} else None


def capture(owner_id, path, data):
    match = PATH.fullmatch(path)
    if not isinstance(data, dict) or not isinstance(data.get("job_id"), str) or not match:
        return None
    status = data.get("status")
    if status not in VALID:
        raise ValueError("Invalid analysis job status")
    with transaction.atomic():
        row = AnalysisJobRecord.objects.select_for_update().filter(pk=data["job_id"]).first()
        if row is not None and row.owner_id != owner_id:
            raise ValueError("Analysis job ownership conflict")
        if row is None:
            exercise_id = data.get("exercise_id")
            if not isinstance(exercise_id, str) or not exercise_id or "progress" not in data:
                return None
            row = AnalysisJobRecord(job_id=data["job_id"], owner_id=owner_id, exercise_id=exercise_id)
        row.status = status
        if "result" in data or status in {"failed", "rejected", "error"}:
            row.outcome = _outcome(data, status)
        for name in (
            "exercise_id", "stage", "error_code", "message", "http_status", "result",
            "engine_version", "model_version", "created_at", "started_at", "completed_at",
        ):
            if name in data:
                setattr(row, name, data[name])
        if "progress" in data:
            row.progress = max(0, min(100, int(data["progress"] or 0)))
        if "attempts" in data:
            row.attempts = max(0, int(data["attempts"] or 0))
        if "max_attempts" in data:
            row.max_attempts = max(0, int(data["max_attempts"] or 0))
        if "cancel_requested" in data:
            row.cancel_requested = bool(data["cancel_requested"])
        if not row.stage:
            row.stage = status
        row.save()
    return row
