"""Metadata-only session persistence models."""

from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import Boolean, DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.database import Base


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


class AnalysisSession(Base):
    __tablename__ = "analysis_sessions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    session_id: Mapped[str] = mapped_column(String(36), unique=True, index=True, nullable=False)
    patient_id: Mapped[str | None] = mapped_column(ForeignKey("patient_profiles.patient_id", ondelete="SET NULL"), index=True)
    owner_user_id: Mapped[str | None] = mapped_column(String(36), index=True)
    created_by_user_id: Mapped[str | None] = mapped_column(String(36), index=True)
    exercise_id: Mapped[str] = mapped_column(String(64), index=True, nullable=False)
    exercise_display_name: Mapped[str] = mapped_column(String(128), nullable=False)
    status: Mapped[str] = mapped_column(String(32), index=True, nullable=False)
    error_code: Mapped[str | None] = mapped_column(String(128))
    message: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, onupdate=utc_now, nullable=False)
    source_filename: Mapped[str | None] = mapped_column(String(255))
    video_duration_sec: Mapped[float | None] = mapped_column(Float)
    total_reps: Mapped[int | None] = mapped_column(Integer)
    movement_score: Mapped[float | None] = mapped_column(Float)
    rep_count_confidence: Mapped[float | None] = mapped_column(Float)
    analysis_confidence_score: Mapped[float | None] = mapped_column(Float)
    analysis_confidence_level: Mapped[str | None] = mapped_column(String(32))
    pose_quality_score: Mapped[float | None] = mapped_column(Float)
    pose_quality_level: Mapped[str | None] = mapped_column(String(32))
    summary: Mapped[str | None] = mapped_column(Text)
    limitations_json: Mapped[str] = mapped_column(Text, default="[]", nullable=False)
    feedback_json: Mapped[str] = mapped_column(Text, default="[]", nullable=False)
    detected_issues_json: Mapped[str] = mapped_column(Text, default="[]", nullable=False)
    score_breakdown_json: Mapped[str] = mapped_column(Text, default="null", nullable=False)
    input_validity_json: Mapped[str] = mapped_column(Text, default="null", nullable=False)
    ml_prediction_json: Mapped[str] = mapped_column(Text, default="null", nullable=False)
    report_id: Mapped[str | None] = mapped_column(String(64))
    report_download_url: Mapped[str | None] = mapped_column(Text)
    overlay_id: Mapped[str | None] = mapped_column(String(64))
    overlay_preview_url: Mapped[str | None] = mapped_column(Text)
    overlay_download_url: Mapped[str | None] = mapped_column(Text)

    metrics: Mapped[list["SessionMetric"]] = relationship(back_populates="session", cascade="all, delete-orphan")
    uploaded_media: Mapped[list["UploadedMedia"]] = relationship(back_populates="session", cascade="all, delete-orphan")
    detected_issue_rows: Mapped[list["DetectedIssue"]] = relationship(back_populates="session", cascade="all, delete-orphan")
    patient: Mapped["PatientProfile | None"] = relationship(back_populates="sessions")


class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[str] = mapped_column(String(36), unique=True, index=True, nullable=False)
    email: Mapped[str] = mapped_column(String(320), unique=True, index=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    full_name: Mapped[str | None] = mapped_column(String(120))
    role: Mapped[str] = mapped_column(String(32), index=True, nullable=False, default="researcher_demo")
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    is_verified: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, onupdate=utc_now, nullable=False)


class UserConsent(Base):
    __tablename__ = "user_consents"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[str] = mapped_column(ForeignKey("users.user_id", ondelete="CASCADE"), index=True)
    consent_type: Mapped[str] = mapped_column(String(64), nullable=False)
    accepted: Mapped[bool] = mapped_column(Boolean, nullable=False)
    accepted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    version: Mapped[str] = mapped_column(String(32), nullable=False)
    notes: Mapped[str | None] = mapped_column(Text)


class AuditLog(Base):
    __tablename__ = "audit_logs"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    actor_user_id: Mapped[str | None] = mapped_column(String(36), index=True)
    action: Mapped[str] = mapped_column(String(128), nullable=False)
    resource_type: Mapped[str] = mapped_column(String(64), nullable=False)
    resource_id: Mapped[str | None] = mapped_column(String(64))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, nullable=False)
    metadata_json: Mapped[str | None] = mapped_column(Text)


class RecognitionEvent(Base):
    """Privacy-safe recognition audit record; uploaded media is never retained here."""

    __tablename__ = "recognition_events"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    event_id: Mapped[str] = mapped_column(String(36), unique=True, index=True, nullable=False)
    actor_user_id: Mapped[str | None] = mapped_column(String(36), index=True)
    model_id: Mapped[str] = mapped_column(String(128), index=True, nullable=False)
    source_type: Mapped[str] = mapped_column(String(32), nullable=False)
    status: Mapped[str] = mapped_column(String(32), index=True, nullable=False)
    predicted_exercise_id: Mapped[str] = mapped_column(String(64), index=True, nullable=False)
    confidence: Mapped[float] = mapped_column(Float, nullable=False)
    confidence_threshold: Mapped[float | None] = mapped_column(Float)
    abstained: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    analyzer_available: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    usable_pose_frames: Mapped[int | None] = mapped_column(Integer)
    confirmed_exercise_id: Mapped[str | None] = mapped_column(String(64), index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, nullable=False)
    confirmed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))


class PatientProfile(Base):
    __tablename__ = "patient_profiles"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    patient_id: Mapped[str] = mapped_column(String(36), unique=True, index=True, nullable=False)
    display_name: Mapped[str] = mapped_column(String(120), nullable=False)
    age_group: Mapped[str | None] = mapped_column(String(32))
    sex: Mapped[str | None] = mapped_column(String(32))
    clinical_group: Mapped[str | None] = mapped_column(String(64))
    notes: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, onupdate=utc_now, nullable=False)
    sessions: Mapped[list[AnalysisSession]] = relationship(back_populates="patient")


class SessionMetric(Base):
    __tablename__ = "session_metrics"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    session_id: Mapped[str] = mapped_column(ForeignKey("analysis_sessions.session_id", ondelete="CASCADE"), index=True)
    metric_name: Mapped[str] = mapped_column(String(128), nullable=False)
    metric_value_float: Mapped[float | None] = mapped_column(Float)
    metric_value_text: Mapped[str | None] = mapped_column(Text)
    unit: Mapped[str | None] = mapped_column(String(32))
    session: Mapped[AnalysisSession] = relationship(back_populates="metrics")


class UploadedMedia(Base):
    __tablename__ = "uploaded_media"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    session_id: Mapped[str | None] = mapped_column(ForeignKey("analysis_sessions.session_id", ondelete="SET NULL"), index=True)
    original_filename: Mapped[str] = mapped_column(String(255), nullable=False)
    stored_path: Mapped[str | None] = mapped_column(Text)
    content_type: Mapped[str | None] = mapped_column(String(128))
    size_bytes: Mapped[int | None] = mapped_column(Integer)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, nullable=False)
    session: Mapped[AnalysisSession | None] = relationship(back_populates="uploaded_media")


class DetectedIssue(Base):
    __tablename__ = "detected_issues"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    session_id: Mapped[str] = mapped_column(ForeignKey("analysis_sessions.session_id", ondelete="CASCADE"), index=True)
    issue_code: Mapped[str] = mapped_column(String(128), nullable=False)
    severity: Mapped[str | None] = mapped_column(String(32))
    message: Mapped[str | None] = mapped_column(Text)
    session: Mapped[AnalysisSession] = relationship(back_populates="detected_issue_rows")
