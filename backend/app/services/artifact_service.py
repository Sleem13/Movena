"""Short-lived local artifact storage for reports and annotated videos."""

from __future__ import annotations

import time
from pathlib import Path
from uuid import UUID, uuid4

from app.core.config import get_settings


ARTIFACT_SUFFIXES = {"report": ".pdf", "overlay": ".mp4"}


def cleanup_expired_artifacts(now: float | None = None) -> int:
    settings = get_settings()
    artifact_dir = settings.artifact_dir
    if not artifact_dir.exists():
        return 0
    cutoff = (now or time.time()) - settings.artifact_ttl_seconds
    removed = 0
    for path in artifact_dir.iterdir():
        if path.is_file() and path.stat().st_mtime < cutoff:
            path.unlink(missing_ok=True)
            removed += 1
    return removed


def create_artifact(kind: str) -> tuple[str, Path]:
    suffix = ARTIFACT_SUFFIXES[kind]
    settings = get_settings()
    settings.artifact_dir.mkdir(parents=True, exist_ok=True)
    cleanup_expired_artifacts()
    artifact_id = uuid4().hex
    return artifact_id, settings.artifact_dir / f"{artifact_id}{suffix}"


def resolve_artifact(artifact_id: str, kind: str) -> Path | None:
    try:
        normalized_id = UUID(artifact_id).hex
    except ValueError:
        return None
    cleanup_expired_artifacts()
    path = get_settings().artifact_dir / f"{normalized_id}{ARTIFACT_SUFFIXES[kind]}"
    return path if path.is_file() else None
