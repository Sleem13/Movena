from fastapi import FastAPI, status
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy.exc import SQLAlchemyError

from app.api.routes.health import router as health_router
from app.api.routes.artifacts import router as artifacts_router
from app.api.routes.squat_analysis import router as squat_router
from app.api.routes.sit_to_stand_analysis import router as sit_to_stand_router
from app.api.routes.knee_extension_analysis import router as knee_extension_router
from app.api.routes.shoulder_abduction_analysis import router as shoulder_abduction_router
from app.api.routes.hip_abduction_analysis import router as hip_abduction_router
from app.api.routes.sessions import router as sessions_router
from app.api.routes.exercise_recognition import router as exercise_recognition_router
from app.api.routes.exercises import router as exercises_router
from app.api.v1.therapist import router as therapist_router
from app.api.v1.auth import router as auth_router
from app.api.dependencies.auth import AuthError
from app.core.config import get_settings
from app.core.cors import cors_middleware_options
from app.services.artifact_service import ensure_artifact_directories
from app.db.database import init_db
from app.core.logging_config import configure_logging
from app.schemas.analysis_schema import ErrorResponse

configure_logging()
settings = get_settings()
settings.validate_deployment_safety()
ensure_artifact_directories()
init_db()

app = FastAPI(
    title=settings.project_name,
    version=settings.version,
    description="Movement-analysis API for the PhysioVision AI educational MVP.",
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


@app.exception_handler(SQLAlchemyError)
async def database_exception_handler(_request, _exc: SQLAlchemyError) -> JSONResponse:
    payload = ErrorResponse(
        error_code="DATABASE_UNAVAILABLE",
        message="The database is temporarily unavailable.",
    )
    return JSONResponse(
        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        content=payload.model_dump(),
    )


@app.exception_handler(AuthError)
async def auth_exception_handler(_request, exc: AuthError) -> JSONResponse:
    payload = ErrorResponse(error_code=exc.error_code, message=exc.message)
    return JSONResponse(status_code=exc.status_code, content=payload.model_dump())

app.add_middleware(
    CORSMiddleware,
    **cors_middleware_options(settings),
)

app.include_router(health_router)
app.include_router(squat_router)
app.include_router(sit_to_stand_router)
app.include_router(knee_extension_router)
app.include_router(shoulder_abduction_router)
app.include_router(hip_abduction_router)
app.include_router(artifacts_router)
app.include_router(exercise_recognition_router)
app.include_router(exercises_router)
app.include_router(auth_router)
if settings.enable_session_history:
    app.include_router(sessions_router)
if settings.enable_therapist_dashboard:
    app.include_router(therapist_router)
