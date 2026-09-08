"""Short-lived local artifact storage for reports and annotated videos."""

from __future__ import annotations

import time
import hashlib
import hmac
import re
from pathlib import Path
from uuid import UUID, uuid4

from app.core import artifact_config
from app.core.config import get_settings


ARTIFACT_SUFFIXES = {"report": ".pdf", "overlay": ".webm"}
ARTIFACT_SUBDIRS = {"report": "reports", "overlay": "overlays"}


def _artifact_signature(artifact_id: str, kind: str, expires: int) -> str:
    payload = f"{kind}:{artifact_id}:{expires}".encode()
    return hmac.new(get_settings().secret_key.encode(), payload, hashlib.sha256).hexdigest()


def artifact_slug(exercise_id: str | None) -> str:
    normalized = re.sub(r"[^a-z0-9]+", "-", (exercise_id or "movement").strip().lower()).strip("-")
    return normalized or "movement"


def artifact_download_filename(exercise_id: str | None, kind: str) -> str:
    suffix = ARTIFACT_SUFFIXES[kind]
    return f"movena-{artifact_slug(exercise_id)}-{kind}{suffix}"


def build_artifact_url(
    path: str,
    artifact_id: str,
    kind: str,
    *,
    exercise_id: str | None = None,
) -> str:
    """Return a short-lived signed URL when analysis artifacts are protected."""
    if exercise_id:
        separator = "&" if "?" in path else "?"
        path = f"{path}{separator}exercise={artifact_slug(exercise_id)}"
    settings = get_settings()
    if not settings.require_auth_for_analysis:
        return path
    expires = int(time.time()) + settings.artifact_ttl_seconds
    signature = _artifact_signature(artifact_id, kind, expires)
    separator = "&" if "?" in path else "?"
    return f"{path}{separator}expires={expires}&signature={signature}"


def valid_artifact_signature(artifact_id: str, kind: str, expires: int | None, signature: str | None) -> bool:
    if expires is None or not signature or expires < int(time.time()):
        return False
    expected = _artifact_signature(artifact_id, kind, expires)
    return hmac.compare_digest(signature, expected)


def ensure_artifact_directories() -> Path:
    root = get_settings().artifact_dir
    if root.resolve() == artifact_config.ARTIFACTS_DIR.resolve():
        artifact_config.ensure_default_artifact_directories()
    else:
        root.mkdir(parents=True, exist_ok=True)
    for subdir in ARTIFACT_SUBDIRS.values():
        (root / subdir).mkdir(parents=True, exist_ok=True)
    return root


def cleanup_expired_artifacts(now: float | None = None) -> int:
    settings = get_settings()
    artifact_dir = settings.artifact_dir
    if not artifact_dir.exists():
        return 0
    cutoff = (now or time.time()) - settings.artifact_ttl_seconds
    removed = 0
    for path in artifact_dir.rglob("*"):
        if path.is_file() and path.stat().st_mtime < cutoff:
            path.unlink(missing_ok=True)
            removed += 1
    return removed


def create_artifact(kind: str) -> tuple[str, Path]:
    suffix = ARTIFACT_SUFFIXES[kind]
    artifact_root = ensure_artifact_directories()
    cleanup_expired_artifacts()
    artifact_id = uuid4().hex
    return artifact_id, artifact_root / ARTIFACT_SUBDIRS[kind] / f"{artifact_id}{suffix}"


def resolve_artifact(artifact_id: str, kind: str) -> Path | None:
    suffix = ARTIFACT_SUFFIXES[kind]
    normalized_input = Path(artifact_id).name
    if normalized_input.lower().endswith(suffix):
        normalized_input = normalized_input[: -len(suffix)]
    try:
        normalized_id = UUID(normalized_input).hex
    except ValueError:
        return None
    cleanup_expired_artifacts()
    path = (
        get_settings().artifact_dir
        / ARTIFACT_SUBDIRS[kind]
        / f"{normalized_id}{suffix}"
    )
    return path if path.is_file() else None
