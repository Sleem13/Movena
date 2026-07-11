from fastapi import FastAPI, status
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api.routes.health import router as health_router
from app.api.routes.squat_analysis import router as squat_router
from app.core.config import get_settings
from app.core.logging_config import configure_logging
from app.schemas.analysis_schema import ErrorResponse

configure_logging()
settings = get_settings()

app = FastAPI(
    title=settings.project_name,
    version=settings.version,
    description="Sprint 1 MVP for AI-assisted squat exercise analysis.",
)


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(_request, exc: RequestValidationError) -> JSONResponse:
    details = [error.get("msg", "Invalid request.") for error in exc.errors()]
    payload = ErrorResponse(
        error_code="MISSING_FILE",
        message="A video file is required.",
        details=details,
    )
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content=payload.model_dump(),
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
