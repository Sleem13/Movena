import os
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, status
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy.exc import OperationalError, SQLAlchemyError

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
from app.api.routes.analysis_jobs import router as analysis_jobs_router
from app.api.routes.ml_models import router as ml_models_router
from app.api.routes.rehab_rl import router as rehab_rl_router
from app.api.v1.therapist import router as therapist_router
from app.api.v1.auth import router as auth_router
from app.api.v1.admin import router as admin_router
from app.api.v1.patient import router as patient_router
from app.api.v1.scheduling import router as scheduling_router
from app.api.v1.catalog import router as catalog_router
from app.api.v1.commerce import router as commerce_router
from app.api.v1.admin_platform import router as admin_platform_router
from app.api.v1.therapist_care import router as therapist_care_router
from app.api.v1.recovery_coaching import router as recovery_coaching_router
from app.api.v1.connections import router as connections_router
from app.api.dependencies.auth import AuthError
from app.core.config import get_settings
from app.core.cors import cors_middleware_options
from app.services.artifact_service import ensure_artifact_directories
from app.services.exercise_recognition_service import initialize_active_recognition_models
from app.services.ml_model_readiness_service import validate_required_ml_models
from app.db.database import init_db, verify_production_schema
from app.core.logging_config import configure_logging
from app.schemas.analysis_schema import ErrorResponse

configure_logging()
logger = logging.getLogger(__name__)
settings = get_settings()
settings.validate_deployment_safety()
validate_required_ml_models(settings.required_ml_exercises)
ensure_artifact_directories()
if settings.app_env == "production":
    verify_production_schema()
else:
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


@asynccontextmanager
async def lifespan(_app: FastAPI):
    if os.getenv("ANALYSIS_JOB_WORKER") != "1":
        from app.services.analysis_job_service import recover_analysis_jobs

        recover_analysis_jobs()
    yield

app = FastAPI(
    title=settings.project_name,
    version=settings.version,
    description="Movement-analysis API for the Movena educational MVP.",
    lifespan=lifespan,
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
async def database_exception_handler(_request, exc: SQLAlchemyError) -> JSONResponse:
    logger.error(
        "Database request failed",
        exc_info=(type(exc), exc, exc.__traceback__),
    )
    detail = str(getattr(exc, "orig", exc)).lower()
    schema_outdated = isinstance(exc, OperationalError) and any(
        marker in detail for marker in ("no such column", "undefined column", "does not exist")
    )
    payload = ErrorResponse(
        error_code="DATABASE_SCHEMA_OUTDATED" if schema_outdated else "DATABASE_UNAVAILABLE",
        message=(
            "The database schema is out of date. Apply the latest migrations and restart the service."
            if schema_outdated
            else "The database is temporarily unavailable."
        ),
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
app.include_router(analysis_jobs_router)
app.include_router(ml_models_router)
app.include_router(rehab_rl_router)
app.include_router(auth_router)
app.include_router(admin_router)
app.include_router(patient_router)
app.include_router(scheduling_router)
app.include_router(catalog_router)
app.include_router(commerce_router)
app.include_router(admin_platform_router)
app.include_router(therapist_care_router)
app.include_router(recovery_coaching_router)
app.include_router(connections_router)
if settings.enable_session_history:
    app.include_router(sessions_router)
if settings.enable_therapist_dashboard:
    app.include_router(therapist_router)
