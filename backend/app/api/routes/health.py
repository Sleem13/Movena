from uuid import uuid4

from fastapi import APIRouter, Response, status
from sqlalchemy import text

from app.core.config import get_settings
from app.db.database import engine
from app.services.artifact_service import ensure_artifact_directories

router = APIRouter(tags=["health"])


def _database_status() -> str:
    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
        return "ok"
    except Exception:
        return "unavailable"


def _artifact_dirs_status() -> str:
    try:
        root = ensure_artifact_directories().resolve()
        probe = root / f".readiness-{uuid4().hex}.tmp"
        probe.write_bytes(b"ok")
        probe.unlink(missing_ok=True)
        return "ok"
    except (OSError, PermissionError):
        return "unavailable"


def _health_payload() -> dict[str, object]:
    settings = get_settings()
    return {
        "status": "ok",
        "project": settings.project_name,
        "version": settings.version,
        "app_version": settings.version,
        "environment": settings.app_env,
        "database_status": _database_status(),
        "artifact_dirs_status": _artifact_dirs_status(),
        "enabled_features": settings.enabled_features,
    }


@router.get("/health")
def health_check() -> dict[str, object]:
    return _health_payload()


@router.get("/ready")
def readiness_check(response: Response) -> dict[str, object]:
    payload = _health_payload()
    database_ok = payload["database_status"] == "ok"
    artifacts_ok = payload["artifact_dirs_status"] == "ok"
    ready = database_ok and artifacts_ok
    if not ready:
        response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE
    return {
        "status": "ready" if ready else "not_ready",
        "database_connection": "ok" if database_ok else "unavailable",
        "artifact_directories": "writable" if artifacts_ok else "unavailable",
        "config_loaded": True,
        "required_models": "available_or_loaded_on_demand",
    }
