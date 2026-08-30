"""Compatibility package for repository-root ASGI launches.

Render and similar hosts commonly run ``uvicorn app.main:app`` from the
repository root.  The actual application package lives in ``backend/app``;
adding that directory to this package's search path keeps that conventional
command working without duplicating the backend package.
"""

import sys
from pathlib import Path


_BACKEND_DIR = Path(__file__).resolve().parents[1] / "backend"
_BACKEND_APP_DIR = _BACKEND_DIR / "app"
if _BACKEND_DIR.is_dir() and str(_BACKEND_DIR) not in sys.path:
    # Backend sibling packages (including the embedded RehabRL engine) must be
    # importable when hosts launch ``app.main:app`` from the repository root.
    sys.path.insert(0, str(_BACKEND_DIR))
if _BACKEND_APP_DIR.is_dir():
    __path__.append(str(_BACKEND_APP_DIR))

