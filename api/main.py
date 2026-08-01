"""Repository-root ASGI entrypoint.

This keeps `python -m uvicorn api.main:app` working when launched from the
project root, while the real backend package remains under `backend/app`.
"""

from __future__ import annotations

import sys
from pathlib import Path

BACKEND_DIR = Path(__file__).resolve().parents[1] / "backend"
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from app.main import app

__all__ = ["app"]
