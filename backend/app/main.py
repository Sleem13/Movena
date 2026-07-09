from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes.health import router as health_router
from app.api.routes.squat_analysis import router as squat_router
from app.core.config import get_settings
from app.core.logging_config import configure_logging

configure_logging()
settings = get_settings()

app = FastAPI(
    title=settings.project_name,
    version=settings.version,
    description="Sprint 1 MVP for AI-assisted squat exercise analysis.",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health_router)
app.include_router(squat_router)
