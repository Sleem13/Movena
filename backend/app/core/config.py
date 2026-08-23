"""Environment-driven application settings without secret-bearing defaults."""

from __future__ import annotations

import os
from functools import lru_cache
from pathlib import Path

from pydantic import BaseModel, Field

from app.core.artifact_config import ARTIFACTS_DIR, BACKEND_ROOT


DEFAULT_CORS_ORIGINS = [
    "http://localhost:5173", "http://127.0.0.1:5173",
    "http://localhost:3000", "http://127.0.0.1:3000",
    "http://localhost:8081", "http://127.0.0.1:8081",
]
DEFAULT_EXTENSIONS = {".mp4", ".mov", ".avi", ".mkv", ".webm"}
DEPLOYMENT_ENVIRONMENTS = {"staging", "production"}
INSECURE_SECRET_KEYS = {"", "change-me-in-production"}
DEFAULT_ACTIVE_SEQUENCE_RECOGNITION_MODEL_ID = "exercise_pose_gru_20260809T161346Z"
DEFAULT_ACTIVE_FRAME_RECOGNITION_MODEL_ID = "exercise_pose_xgb_20260809T154328Z"


def normalize_database_url(value: str) -> str:
    """Select Psycopg 3 for common provider-style PostgreSQL URLs."""
    if value.startswith("postgres://"):
        return "postgresql+psycopg://" + value[len("postgres://"):]
    if value.startswith("postgresql://"):
        return "postgresql+psycopg://" + value[len("postgresql://"):]
    return value


def _csv(value: str | None, default: list[str]) -> list[str]:
    return [item.strip() for item in (value or ",".join(default)).split(",") if item.strip()]


def _bool(name: str, default: bool) -> bool:
    return os.getenv(name, str(default)).strip().lower() in {"1", "true", "yes", "on"}


class Settings(BaseModel):
    project_name: str = "PhysioVision AI"
    version: str = "0.12.0"
    api_v1_prefix: str = "/api/v1"
    app_env: str = "development"
    api_host: str = "127.0.0.1"
    api_port: int = Field(default=8000, ge=1, le=65535)
    database_url: str = "sqlite:///./physiovision_dev.db"
    cors_allowed_origins: list[str] = Field(default_factory=lambda: list(DEFAULT_CORS_ORIGINS))
    upload_dir: Path = BACKEND_ROOT / "tmp/uploads"
    artifact_dir: Path = ARTIFACTS_DIR
    artifact_retention_hours: float = 24.0
    artifact_ttl_seconds: int = 24 * 60 * 60
    max_upload_size_mb: int = 100
    max_upload_size_bytes: int = 100 * 1024 * 1024
    max_frame_analysis_rows: int = 300
    min_readable_video_frames: int = 3
    min_landmark_visibility: float = 0.45
    enable_subject_continuity_guard: bool = True
    subject_min_visibility: float = Field(default=0.5, ge=0, le=1)
    subject_max_centroid_jump: float = Field(default=0.16, gt=0, le=1)
    subject_severe_centroid_jump: float = Field(default=0.24, gt=0, le=1)
    subject_max_scale_ratio: float = Field(default=1.85, gt=1)
    subject_switch_event_limit: int = Field(default=2, ge=1)
    subject_max_tracking_gap_frames: int = Field(default=10, ge=0)
    pose_backend: str = "mediapipe"
    pose_target_fps: float = Field(default=12.0, gt=0, le=60)
    allowed_video_extensions: set[str] = Field(default_factory=lambda: set(DEFAULT_EXTENSIONS))
    allowed_video_mime_types: set[str] = {
        "video/mp4", "video/quicktime", "video/x-msvideo", "video/x-matroska",
        "video/webm", "application/octet-stream",
    }
    enable_session_history: bool = True
    enable_therapist_dashboard: bool = True
    enable_ml_second_opinion: bool = True
    enable_exercise_recognition: bool = True
    enable_report_generation: bool = True
    enable_overlay_generation: bool = True
    enable_public_demo_mode: bool = False
    require_auth_for_analysis: bool = False
    active_sequence_recognition_model_id: str = DEFAULT_ACTIVE_SEQUENCE_RECOGNITION_MODEL_ID
    active_frame_recognition_model_id: str = DEFAULT_ACTIVE_FRAME_RECOGNITION_MODEL_ID
    secret_key: str = "change-me-in-production"
    access_token_expire_minutes: int = 60
    jwt_algorithm: str = "HS256"

    @classmethod
    def from_environment(cls) -> "Settings":
        max_mb = int(os.getenv("MAX_UPLOAD_SIZE_MB", "100"))
        retention = float(os.getenv("ARTIFACT_RETENTION_HOURS", "24"))
        extensions = {
            item if item.startswith(".") else f".{item}"
            for item in _csv(os.getenv("ALLOWED_VIDEO_EXTENSIONS"), sorted(DEFAULT_EXTENSIONS))
        }
        return cls(
            version=os.getenv("APP_VERSION", "0.12.0").strip(),
            app_env=os.getenv("APP_ENV", "development").strip().lower(),
            api_host=os.getenv("API_HOST", "127.0.0.1"),
            api_port=int(os.getenv("API_PORT", "8000")),
            database_url=normalize_database_url(os.getenv("DATABASE_URL", "sqlite:///./physiovision_dev.db")),
            cors_allowed_origins=_csv(os.getenv("CORS_ALLOWED_ORIGINS"), DEFAULT_CORS_ORIGINS),
            max_upload_size_mb=max_mb, max_upload_size_bytes=max_mb * 1024 * 1024,
            artifact_retention_hours=retention, artifact_ttl_seconds=round(retention * 3600),
            allowed_video_extensions={item.lower() for item in extensions},
            pose_backend=os.getenv("POSE_BACKEND", "mediapipe").strip().lower(),
            pose_target_fps=float(os.getenv("POSE_TARGET_FPS", "12")),
            enable_subject_continuity_guard=_bool("ENABLE_SUBJECT_CONTINUITY_GUARD", True),
            subject_min_visibility=float(os.getenv("SUBJECT_MIN_VISIBILITY", "0.5")),
            subject_max_centroid_jump=float(os.getenv("SUBJECT_MAX_CENTROID_JUMP", "0.16")),
            subject_severe_centroid_jump=float(os.getenv("SUBJECT_SEVERE_CENTROID_JUMP", "0.24")),
            subject_max_scale_ratio=float(os.getenv("SUBJECT_MAX_SCALE_RATIO", "1.85")),
            subject_switch_event_limit=int(os.getenv("SUBJECT_SWITCH_EVENT_LIMIT", "2")),
            subject_max_tracking_gap_frames=int(os.getenv("SUBJECT_MAX_TRACKING_GAP_FRAMES", "10")),
            enable_session_history=_bool("ENABLE_SESSION_HISTORY", True),
            enable_therapist_dashboard=_bool("ENABLE_THERAPIST_DASHBOARD", True),
            enable_ml_second_opinion=_bool("ENABLE_ML_SECOND_OPINION", True),
            enable_exercise_recognition=_bool(
                "ENABLE_EXERCISE_RECOGNITION",
                _bool("ENABLE_ML_SECOND_OPINION", True),
            ),
            enable_report_generation=_bool("ENABLE_REPORT_GENERATION", True),
            enable_overlay_generation=_bool("ENABLE_OVERLAY_GENERATION", True),
            enable_public_demo_mode=_bool("ENABLE_PUBLIC_DEMO_MODE", False),
            require_auth_for_analysis=_bool("REQUIRE_AUTH_FOR_ANALYSIS", False),
            active_sequence_recognition_model_id=os.getenv(
                "ACTIVE_SEQUENCE_RECOGNITION_MODEL_ID",
                DEFAULT_ACTIVE_SEQUENCE_RECOGNITION_MODEL_ID,
            ).strip(),
            active_frame_recognition_model_id=os.getenv(
                "ACTIVE_FRAME_RECOGNITION_MODEL_ID",
                DEFAULT_ACTIVE_FRAME_RECOGNITION_MODEL_ID,
            ).strip(),
            secret_key=os.getenv("SECRET_KEY", "change-me-in-production"),
            access_token_expire_minutes=int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "60")),
            jwt_algorithm=os.getenv("JWT_ALGORITHM", "HS256"),
        )

    @property
    def enabled_features(self) -> dict[str, bool]:
        return {
            "session_history": self.enable_session_history,
            "therapist_dashboard": self.enable_therapist_dashboard,
            "ml_second_opinion": self.enable_ml_second_opinion,
            "exercise_recognition": self.enable_exercise_recognition,
            "report_generation": self.enable_report_generation,
            "overlay_generation": self.enable_overlay_generation,
            "subject_continuity_guard": self.enable_subject_continuity_guard,
            "public_demo_mode": self.enable_public_demo_mode,
            "auth_required_for_analysis": self.require_auth_for_analysis,
        }

    @property
    def effective_cors_origins(self) -> list[str]:
        """Return deployable origins; wildcard CORS is never enabled outside development."""
        if self.app_env in DEPLOYMENT_ENVIRONMENTS:
            return [origin for origin in self.cors_allowed_origins if origin != "*"]
        return self.cors_allowed_origins

    def validate_deployment_safety(self) -> None:
        """Fail closed when staging/production starts with development security settings."""
        if self.app_env not in DEPLOYMENT_ENVIRONMENTS:
            return
        issues: list[str] = []
        if self.secret_key in INSECURE_SECRET_KEYS or len(self.secret_key) < 32:
            issues.append("SECRET_KEY must be a non-default value of at least 32 characters")
        if not self.cors_allowed_origins or "*" in self.cors_allowed_origins:
            issues.append("CORS_ALLOWED_ORIGINS must contain explicit origins and cannot include '*'")
        if any(not origin.startswith("https://") for origin in self.effective_cors_origins):
            issues.append("staging/production CORS origins must use HTTPS")
        if not self.require_auth_for_analysis:
            issues.append("REQUIRE_AUTH_FOR_ANALYSIS must be true")
        if self.enable_public_demo_mode:
            issues.append("ENABLE_PUBLIC_DEMO_MODE must be false")
        if not self.enable_subject_continuity_guard:
            issues.append("ENABLE_SUBJECT_CONTINUITY_GUARD must be true")
        if issues:
            raise RuntimeError("Unsafe deployment configuration: " + "; ".join(issues))


@lru_cache
def get_settings() -> Settings:
    return Settings.from_environment()
