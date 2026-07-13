"""Canonical filesystem locations for temporary backend artifacts."""

from pathlib import Path


BACKEND_ROOT = Path(__file__).resolve().parents[2]
ARTIFACTS_DIR = BACKEND_ROOT / "artifacts"
OVERLAYS_DIR = ARTIFACTS_DIR / "overlays"
REPORTS_DIR = ARTIFACTS_DIR / "reports"


def ensure_default_artifact_directories() -> None:
    """Create the canonical artifact tree when the backend starts."""
    for directory in (ARTIFACTS_DIR, OVERLAYS_DIR, REPORTS_DIR):
        directory.mkdir(parents=True, exist_ok=True)
