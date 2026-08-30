"""FastAPI application factory and delivery-layer configuration."""

from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

from rehabrl.config import PROJECT_ROOT

from .errors import (
    CheckpointLoadError,
    CheckpointNotFoundError,
    InvalidInjuryError,
    RehabRLServiceError,
    TrainingInProgressError,
)
from .routes import create_api_router
from .service import RehabRLService

ALLOWED_DEVELOPMENT_ORIGINS = (
    "http://localhost:5173",
    "http://127.0.0.1:5173",
)
SERVICE_ERROR_STATUS = {
    InvalidInjuryError: 400,
    CheckpointNotFoundError: 404,
    CheckpointLoadError: 422,
    TrainingInProgressError: 409,
}


def create_app(project_root: Path | None = None) -> FastAPI:
    """Build a configured RehabRL application."""
    root = project_root or PROJECT_ROOT
    frontend_dist = root / "frontend" / "dist"
    service = RehabRLService(root)

    app = FastAPI(title="RehabRL API", version="1.0.0")
    app.state.rehabrl_service = service
    app.add_middleware(
        CORSMiddleware,
        allow_origins=list(ALLOWED_DEVELOPMENT_ORIGINS),
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    _register_error_handlers(app)
    app.include_router(create_api_router(service))
    _mount_frontend(app, frontend_dist)
    return app


def _register_error_handlers(app: FastAPI) -> None:
    @app.exception_handler(RehabRLServiceError)
    async def handle_service_error(
        _request: Request,
        error: RehabRLServiceError,
    ) -> JSONResponse:
        return JSONResponse(
            status_code=SERVICE_ERROR_STATUS[type(error)],
            content={"detail": str(error)},
        )


def _mount_frontend(app: FastAPI, frontend_dist: Path) -> None:
    if not frontend_dist.exists():
        return

    assets = frontend_dist / "assets"
    if assets.exists():
        app.mount("/assets", StaticFiles(directory=assets), name="assets")

    resolved_dist = frontend_dist.resolve()

    @app.get("/{full_path:path}", include_in_schema=False)
    def frontend(full_path: str) -> FileResponse:
        requested = (resolved_dist / full_path).resolve()
        if full_path and requested.is_file() and resolved_dist in requested.parents:
            return FileResponse(requested)
        return FileResponse(resolved_dist / "index.html")
