import os

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
from app.api.routes.gait_analysis import router as gait_router
from app.api.routes.balance_analysis import router as balance_router
from app.api.routes.upper_body_analysis import router as upper_body_router
from app.api.routes.sessions import router as sessions_router
from app.api.routes.exercise_recognition import router as exercise_recognition_router
from app.api.routes.exercises import router as exercises_router
from app.api.routes.realtime_coaching import router as realtime_coaching_router
from app.api.v1.therapist import router as therapist_router
from app.api.v1.auth import router as auth_router
from app.api.v1.admin import router as admin_router
from app.api.dependencies.auth import AuthError
from app.core.config import get_settings
from app.core.cors import cors_middleware_options
from app.services.artifact_service import ensure_artifact_directories
from app.services.exercise_recognition_service import initialize_active_recognition_models
from app.db.database import init_db
from app.core.logging_config import configure_logging
from app.schemas.analysis_schema import ErrorResponse

configure_logging()
settings = get_settings()
settings.validate_deployment_safety()
ensure_artifact_directories()
init_db()
if settings.enable_exercise_recognition:
    initialize_active_recognition_models(
        settings,
        strict=settings.app_env in {"staging", "production"},
    )
if os.getenv("SEED_ADMIN_ON_START", "").strip().lower() in {"1", "true", "yes", "on"}:
    from app.services.admin_seed_service import seed_admin_from_environment

    # Startup seeding is intentionally non-destructive: deployments never rewrite an existing role.
    seed_admin_from_environment(reset=False)
if os.getenv("SEED_SUPER_ADMIN_ON_START", "").strip().lower() in {"1", "true", "yes", "on"}:
    from app.services.admin_seed_service import seed_super_admin_from_environment

    seed_super_admin_from_environment(reset=False)

app = FastAPI(
    title=settings.project_name,
    version=settings.version,
    description="Movement-analysis API for the PhysioVision AI educational MVP.",
)


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(_request, exc: RequestValidationError) -> JSONResponse:
    errors = exc.errors()
    missing_video = any(
        error.get("type") == "missing"
        and tuple(error.get("loc", ()))[:1] == ("body",)
        and tuple(error.get("loc", ()))[-1:] == ("video",)
        for error in errors
    )
    details = []
    for error in errors:
        field = ".".join(str(part) for part in error.get("loc", ()) if part not in {"body", "query", "path"})
        label = field.replace("_", " ").capitalize()
        error_type = error.get("type")
        context = error.get("ctx", {})
        if field and error_type == "missing":
            detail = f"{label} is required."
        elif field and error_type == "string_too_short":
            detail = f"{label} must be at least {context.get('min_length')} characters."
        elif field and error_type == "string_too_long":
            detail = f"{label} must be at most {context.get('max_length')} characters."
        else:
            message = error.get("msg", "Invalid value.").removeprefix("Value error, ")
            detail = f"{label}: {message}" if field else message
        details.append(detail)
    if missing_video:
        payload = ErrorResponse(
            error_code="MISSING_FILE",
            message="A video file is required.",
            details=details,
        )
    else:
        payload = ErrorResponse(
            error_code="VALIDATION_ERROR",
            message=details[0] if details else "The submitted information is invalid.",
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
app.include_router(gait_router)
app.include_router(balance_router)
app.include_router(upper_body_router)
app.include_router(artifacts_router)
if settings.enable_exercise_recognition:
    app.include_router(exercise_recognition_router)
app.include_router(exercises_router)
app.include_router(realtime_coaching_router)
app.include_router(auth_router)
app.include_router(admin_router)
if settings.enable_session_history:
    app.include_router(sessions_router)
if settings.enable_therapist_dashboard:
    app.include_router(therapist_router)
