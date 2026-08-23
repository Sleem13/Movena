"""Compatibility package for repository-root ASGI launches.

Render and similar hosts commonly run ``uvicorn app.main:app`` from the
repository root.  The actual application package lives in ``backend/app``;
adding that directory to this package's search path keeps that conventional
command working without duplicating the backend package.
"""

from pathlib import Path


_BACKEND_APP_DIR = Path(__file__).resolve().parents[1] / "backend" / "app"
if _BACKEND_APP_DIR.is_dir():
    __path__.append(str(_BACKEND_APP_DIR))

