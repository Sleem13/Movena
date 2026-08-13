"""ASGI compatibility entrypoint for ``uvicorn api.main:app``.

The backend's canonical application lives in :mod:`app.main`. This module keeps
the repository's legacy Uvicorn command working when the current directory is
``backend``.
"""

from app.main import app

__all__ = ["app"]
