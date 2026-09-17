"""Metadata-only session persistence models."""

from __future__ import annotations

from datetime import date, datetime, timezone

import json

from sqlalchemy import (
    Boolean, CheckConstraint, Date, DateTime, Float, ForeignKey, Integer,
    String, Text, UniqueConstraint, text,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.database import Base


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


class AnalysisSession(Base):
    __tablename__ = "analysis_sessions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    session_id: Mapped[str] = mapped_column(String(36), unique=True, index=True, nullable=False)
    patient_id: Mapped[str | None] = mapped_column(ForeignKey("patient_profiles.patient_id", ondelete="SET NULL"), index=True)
    plan_item_id: Mapped[str | None] = mapped_column(
        ForeignKey("exercise_plan_items.item_id", ondelete="SET NULL", name="fk_analysis_sessions_plan_item"), index=True
    )
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


class AnalysisJob(Base):
    """Durable ownership and lifecycle record for background video analysis."""

    __tablename__ = "analysis_jobs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    job_id: Mapped[str] = mapped_column(String(36), unique=True, index=True, nullable=False)
    owner_user_id: Mapped[str] = mapped_column(String(36), index=True, nullable=False)
    exercise_id: Mapped[str] = mapped_column(String(64), index=True, nullable=False)
    status: Mapped[str] = mapped_column(String(24), index=True, nullable=False, default="queued")
    stage: Mapped[str] = mapped_column(String(64), nullable=False, default="queued")
    progress: Mapped[int] = mapped_column(Integer, nullable=False, default=5)
    source_path: Mapped[str] = mapped_column(Text, nullable=False)
    source_filename: Mapped[str] = mapped_column(String(255), nullable=False)
    content_type: Mapped[str | None] = mapped_column(String(128))
    options_json: Mapped[str] = mapped_column(Text, default="{}", nullable=False)
    result_json: Mapped[str | None] = mapped_column(Text)
    error_code: Mapped[str | None] = mapped_column(String(128))
    message: Mapped[str | None] = mapped_column(Text)
    http_status: Mapped[int | None] = mapped_column(Integer)
    cancel_requested: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    attempts: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    max_attempts: Mapped[int] = mapped_column(Integer, default=2, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, nullable=False)
    started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, onupdate=utc_now, nullable=False)


class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[str] = mapped_column(String(36), unique=True, index=True, nullable=False)
    username: Mapped[str | None] = mapped_column(String(64), unique=True, index=True)
    email: Mapped[str] = mapped_column(String(320), unique=True, index=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    identity_owner: Mapped[str] = mapped_column(String(16), default="legacy", server_default="legacy", nullable=False)
    full_name: Mapped[str | None] = mapped_column(String(120))
    role: Mapped[str] = mapped_column(String(32), index=True, nullable=False, default="researcher_demo")
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    is_verified: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    account_status: Mapped[str] = mapped_column(String(32), default="active", server_default="active", nullable=False)
    is_protected: Mapped[bool] = mapped_column(Boolean, default=False, server_default=text("false"), nullable=False)
    token_version: Mapped[int] = mapped_column(Integer, default=0, server_default="0", nullable=False)
    permissions_json: Mapped[str] = mapped_column(Text, default="[]", server_default="[]", nullable=False)
    email_verified_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    verification_token_hash: Mapped[str | None] = mapped_column(String(64), unique=True, index=True)
    verification_token_expires: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    verification_sent_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    reset_password_token_hash: Mapped[str | None] = mapped_column(String(64), unique=True, index=True)
    reset_password_expires: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    reset_password_sent_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, onupdate=utc_now, nullable=False)

    @property
    def permissions(self) -> list[str]:
        try:
            value = json.loads(self.permissions_json)
            return value if isinstance(value, list) else []
        except (TypeError, json.JSONDecodeError):
            return []


class UserConsent(Base):
    __tablename__ = "user_consents"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[str] = mapped_column(ForeignKey("users.user_id", ondelete="CASCADE"), index=True)
    consent_type: Mapped[str] = mapped_column(String(64), nullable=False)
    accepted: Mapped[bool] = mapped_column(Boolean, nullable=False)
    accepted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    version: Mapped[str] = mapped_column(String(32), nullable=False)
    notes: Mapped[str | None] = mapped_column(Text)


class InternalPrincipalNonce(Base):
    """Durable one-use record for a signed platform-to-legacy assertion."""

    __tablename__ = "internal_principal_nonces"
    jti: Mapped[str] = mapped_column(String(64), primary_key=True)
    subject: Mapped[str] = mapped_column(String(64), nullable=False)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True, nullable=False)
    consumed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)


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
    user_id: Mapped[str | None] = mapped_column(
        ForeignKey("users.user_id", ondelete="SET NULL"), unique=True, index=True
    )
    display_name: Mapped[str] = mapped_column(String(120), nullable=False)
    age_group: Mapped[str | None] = mapped_column(String(32))
    sex: Mapped[str | None] = mapped_column(String(32))
    clinical_group: Mapped[str | None] = mapped_column(String(64))
    notes: Mapped[str | None] = mapped_column(Text)
    preferred_locale: Mapped[str] = mapped_column(String(8), default="ar", nullable=False)
    timezone_name: Mapped[str] = mapped_column(String(64), default="Africa/Cairo", nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, onupdate=utc_now, nullable=False)
    sessions: Mapped[list[AnalysisSession]] = relationship(back_populates="patient")
    exercise_plans: Mapped[list["ExercisePlan"]] = relationship(
        back_populates="patient", cascade="all, delete-orphan"
    )


class ExercisePlan(Base):
    __tablename__ = "exercise_plans"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    plan_id: Mapped[str] = mapped_column(String(36), unique=True, index=True, nullable=False)
    patient_id: Mapped[str] = mapped_column(
        ForeignKey("patient_profiles.patient_id", ondelete="CASCADE"), index=True, nullable=False
    )
    created_by_user_id: Mapped[str | None] = mapped_column(String(36), index=True)
    title: Mapped[str] = mapped_column(String(120), nullable=False)
    notes: Mapped[str | None] = mapped_column(Text)
    status: Mapped[str] = mapped_column(String(24), index=True, nullable=False, default="active")
    start_date: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    end_date: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utc_now, onupdate=utc_now, nullable=False
    )

    patient: Mapped[PatientProfile] = relationship(back_populates="exercise_plans")
    items: Mapped[list["ExercisePlanItem"]] = relationship(
        back_populates="plan", cascade="all, delete-orphan", order_by="ExercisePlanItem.sort_order"
    )


class ExercisePlanItem(Base):
    __tablename__ = "exercise_plan_items"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    item_id: Mapped[str] = mapped_column(String(36), unique=True, index=True, nullable=False)
    plan_id: Mapped[str] = mapped_column(
        ForeignKey("exercise_plans.plan_id", ondelete="CASCADE"), index=True, nullable=False
    )
    exercise_id: Mapped[str] = mapped_column(String(64), index=True, nullable=False)
    sets: Mapped[int] = mapped_column(Integer, nullable=False)
    reps: Mapped[int] = mapped_column(Integer, nullable=False)
    days_per_week: Mapped[int] = mapped_column(Integer, nullable=False)
    instructions: Mapped[str | None] = mapped_column(Text)
    duration_minutes: Mapped[int | None] = mapped_column(Integer)
    rest_interval_seconds: Mapped[int | None] = mapped_column(Integer)
    tempo: Mapped[str | None] = mapped_column(String(64))
    precautions: Mapped[str | None] = mapped_column(Text)
    target_rom_degrees: Mapped[float | None] = mapped_column(Float)
    target_score: Mapped[float | None] = mapped_column(Float)
    schedule_days_json: Mapped[str] = mapped_column(Text, default="[]", nullable=False)
    requested_media_upload: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    requires_ai_analysis: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    status: Mapped[str] = mapped_column(String(24), default="active", index=True, nullable=False)
    sort_order: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    plan: Mapped[ExercisePlan] = relationship(back_populates="items")


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


class PatientHealthProfile(Base):
    __tablename__ = "patient_health_profiles"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    patient_id: Mapped[str] = mapped_column(
        ForeignKey("patient_profiles.patient_id", ondelete="CASCADE"), unique=True, index=True
    )
    emergency_contact_name: Mapped[str | None] = mapped_column(String(120))
    emergency_contact_phone: Mapped[str | None] = mapped_column(String(32))
    medical_summary: Mapped[str | None] = mapped_column(Text)
    precautions: Mapped[str | None] = mapped_column(Text)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utc_now, onupdate=utc_now, nullable=False
    )


class RecoveryCoachingGoal(Base):
    __tablename__ = "recovery_coaching_goals"
    __table_args__ = (
        CheckConstraint("confidence >= 1 AND confidence <= 5", name="ck_coaching_goal_confidence"),
        CheckConstraint("progress_percent >= 0 AND progress_percent <= 100", name="ck_coaching_goal_progress"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    goal_id: Mapped[str] = mapped_column(String(36), unique=True, index=True, nullable=False)
    patient_id: Mapped[str] = mapped_column(
        ForeignKey("patient_profiles.patient_id", ondelete="CASCADE"), index=True, nullable=False
    )
    created_by_user_id: Mapped[str] = mapped_column(String(36), index=True, nullable=False)
    domain: Mapped[str] = mapped_column(String(32), index=True, nullable=False)
    title: Mapped[str] = mapped_column(String(120), nullable=False)
    specific_action: Mapped[str] = mapped_column(Text, nullable=False)
    measurement: Mapped[str] = mapped_column(String(160), nullable=False)
    why_important: Mapped[str] = mapped_column(Text, nullable=False)
    target_date: Mapped[date] = mapped_column(Date, index=True, nullable=False)
    confidence: Mapped[int] = mapped_column(Integer, nullable=False)
    progress_percent: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    status: Mapped[str] = mapped_column(String(24), default="proposed", index=True, nullable=False)
    patient_agreed: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utc_now, onupdate=utc_now, nullable=False
    )


class RecoveryCoachingCheckIn(Base):
    __tablename__ = "recovery_coaching_check_ins"
    __table_args__ = (
        UniqueConstraint("patient_id", "check_in_date", name="uq_recovery_coaching_daily_check_in"),
        CheckConstraint("energy >= 1 AND energy <= 5", name="ck_coaching_checkin_energy"),
        CheckConstraint("sleep_quality >= 1 AND sleep_quality <= 5", name="ck_coaching_checkin_sleep"),
        CheckConstraint("stress >= 1 AND stress <= 5", name="ck_coaching_checkin_stress"),
        CheckConstraint("recovery_confidence >= 1 AND recovery_confidence <= 5", name="ck_coaching_checkin_confidence"),
        CheckConstraint("activity_minutes >= 0 AND activity_minutes <= 1440", name="ck_coaching_checkin_activity"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    check_in_id: Mapped[str] = mapped_column(String(36), unique=True, index=True, nullable=False)
    patient_id: Mapped[str] = mapped_column(
        ForeignKey("patient_profiles.patient_id", ondelete="CASCADE"), index=True, nullable=False
    )
    created_by_user_id: Mapped[str] = mapped_column(String(36), index=True, nullable=False)
    check_in_date: Mapped[date] = mapped_column(Date, index=True, nullable=False)
    energy: Mapped[int] = mapped_column(Integer, nullable=False)
    sleep_quality: Mapped[int] = mapped_column(Integer, nullable=False)
    stress: Mapped[int] = mapped_column(Integer, nullable=False)
    recovery_confidence: Mapped[int] = mapped_column(Integer, nullable=False)
    activity_minutes: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    barrier_category: Mapped[str] = mapped_column(String(32), default="none", index=True, nullable=False)
    barrier_note: Mapped[str | None] = mapped_column(Text)
    symptoms_changed: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    urgent_concern: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    coaching_state: Mapped[str] = mapped_column(String(24), index=True, nullable=False)
    supportive_prompt: Mapped[str] = mapped_column(Text, nullable=False)
    reviewed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), index=True)
    reviewed_by_user_id: Mapped[str | None] = mapped_column(String(36), index=True)
    review_disposition: Mapped[str | None] = mapped_column(String(40), index=True)
    review_note: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, nullable=False)


class RecoveryCoachingActionPlan(Base):
    __tablename__ = "recovery_coaching_action_plans"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    action_plan_id: Mapped[str] = mapped_column(String(36), unique=True, index=True, nullable=False)
    goal_id: Mapped[str] = mapped_column(
        ForeignKey("recovery_coaching_goals.goal_id", ondelete="CASCADE"), index=True, nullable=False
    )
    patient_id: Mapped[str] = mapped_column(
        ForeignKey("patient_profiles.patient_id", ondelete="CASCADE"), index=True, nullable=False
    )
    created_by_user_id: Mapped[str] = mapped_column(String(36), index=True, nullable=False)
    action_step: Mapped[str] = mapped_column(Text, nullable=False)
    frequency: Mapped[str] = mapped_column(String(120), nullable=False)
    support_needed: Mapped[str | None] = mapped_column(Text)
    review_date: Mapped[date] = mapped_column(Date, index=True, nullable=False)
    patient_agreed: Mapped[bool] = mapped_column(Boolean, nullable=False)
    status: Mapped[str] = mapped_column(String(24), default="active", index=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utc_now, onupdate=utc_now, nullable=False
    )


class RecoveryCoachingReminderPreference(Base):
    __tablename__ = "recovery_coaching_reminder_preferences"
    __table_args__ = (
        UniqueConstraint("patient_id", name="uq_recovery_coaching_reminder_patient"),
        CheckConstraint("missed_follow_up_days >= 1 AND missed_follow_up_days <= 14", name="ck_coaching_missed_follow_up_days"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    preference_id: Mapped[str] = mapped_column(String(36), unique=True, index=True, nullable=False)
    patient_id: Mapped[str] = mapped_column(
        ForeignKey("patient_profiles.patient_id", ondelete="CASCADE"), index=True, nullable=False
    )
    enabled: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    local_time: Mapped[str] = mapped_column(String(5), default="19:00", nullable=False)
    cadence: Mapped[str] = mapped_column(String(16), default="daily", nullable=False)
    missed_follow_up_days: Mapped[int] = mapped_column(Integer, default=3, nullable=False)
    patient_agreed: Mapped[bool] = mapped_column(Boolean, nullable=False)
    created_by_user_id: Mapped[str] = mapped_column(String(36), index=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utc_now, onupdate=utc_now, nullable=False
    )


class TherapistPatientAssignment(Base):
    __tablename__ = "therapist_patient_assignments"
    __table_args__ = (
        UniqueConstraint("therapist_user_id", "patient_id", name="uq_therapist_patient_assignment"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    assignment_id: Mapped[str] = mapped_column(String(36), unique=True, index=True, nullable=False)
    therapist_user_id: Mapped[str] = mapped_column(
        ForeignKey("users.user_id", ondelete="CASCADE"), index=True, nullable=False
    )
    patient_id: Mapped[str] = mapped_column(
        ForeignKey("patient_profiles.patient_id", ondelete="CASCADE"), index=True, nullable=False
    )
    status: Mapped[str] = mapped_column(String(24), default="active", index=True, nullable=False)
    assigned_by_user_id: Mapped[str | None] = mapped_column(String(36), index=True)
    assigned_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, nullable=False)
    source: Mapped[str] = mapped_column(String(24), default="legacy", server_default="legacy", nullable=False)
    ended_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    ended_by_user_id: Mapped[str | None] = mapped_column(String(36))
    end_reason: Mapped[str | None] = mapped_column(Text)


class CareInvitation(Base):
    __tablename__ = "care_invitations"
    __table_args__ = (UniqueConstraint("therapist_user_id", "email", name="uq_care_invitation_recipient"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    invitation_id: Mapped[str] = mapped_column(String(36), unique=True, nullable=False)
    therapist_user_id: Mapped[str] = mapped_column(ForeignKey("users.user_id"), index=True, nullable=False)
    email: Mapped[str] = mapped_column(String(320), index=True, nullable=False)
    patient_id: Mapped[str | None] = mapped_column(ForeignKey("patient_profiles.patient_id"))
    token_hash: Mapped[str | None] = mapped_column(String(64), unique=True)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    status: Mapped[str] = mapped_column(String(24), default="pending", nullable=False)
    delivery_status: Mapped[str] = mapped_column(String(24), default="pending", nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, onupdate=utc_now, nullable=False)


class AdherenceEntry(Base):
    __tablename__ = "adherence_entries"
    __table_args__ = (
        UniqueConstraint("patient_id", "plan_item_id", "scheduled_date", name="uq_daily_adherence"),
        CheckConstraint("pain_before IS NULL OR (pain_before >= 0 AND pain_before <= 10)", name="ck_pain_before"),
        CheckConstraint("pain_after IS NULL OR (pain_after >= 0 AND pain_after <= 10)", name="ck_pain_after"),
        CheckConstraint("difficulty IS NULL OR (difficulty >= 1 AND difficulty <= 5)", name="ck_difficulty"),
        CheckConstraint("fatigue IS NULL OR (fatigue >= 1 AND fatigue <= 5)", name="ck_fatigue"),
        CheckConstraint("perceived_exertion IS NULL OR (perceived_exertion >= 0 AND perceived_exertion <= 10)", name="ck_perceived_exertion"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    adherence_id: Mapped[str] = mapped_column(String(36), unique=True, index=True, nullable=False)
    patient_id: Mapped[str] = mapped_column(
        ForeignKey("patient_profiles.patient_id", ondelete="CASCADE"), index=True, nullable=False
    )
    plan_item_id: Mapped[str] = mapped_column(
        ForeignKey("exercise_plan_items.item_id", ondelete="CASCADE"), index=True, nullable=False
    )
    scheduled_date: Mapped[date] = mapped_column(Date, index=True, nullable=False)
    completion_status: Mapped[str] = mapped_column(String(24), nullable=False)
    pain_before: Mapped[int | None] = mapped_column(Integer)
    pain_after: Mapped[int | None] = mapped_column(Integer)
    difficulty: Mapped[int | None] = mapped_column(Integer)
    fatigue: Mapped[int | None] = mapped_column(Integer)
    perceived_exertion: Mapped[int | None] = mapped_column(Integer)
    symptoms_changed: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    stopped_due_to_symptoms: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    symptom_flags_json: Mapped[str] = mapped_column(Text, default="[]", nullable=False)
    response_state: Mapped[str] = mapped_column(String(32), default="not_assessed", index=True, nullable=False)
    supportive_instruction: Mapped[str | None] = mapped_column(Text)
    clinician_review_required: Mapped[bool] = mapped_column(Boolean, default=False, index=True, nullable=False)
    reviewed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    reviewed_by_user_id: Mapped[str | None] = mapped_column(String(36), index=True)
    review_disposition: Mapped[str | None] = mapped_column(String(40), index=True)
    review_note: Mapped[str | None] = mapped_column(Text)
    note: Mapped[str | None] = mapped_column(Text)
    analysis_session_id: Mapped[str | None] = mapped_column(
        ForeignKey("analysis_sessions.session_id", ondelete="SET NULL", name="fk_adherence_entries_analysis_session"), index=True
    )
    media_storage_key: Mapped[str | None] = mapped_column(Text)
    idempotency_key: Mapped[str | None] = mapped_column(String(128), unique=True, index=True)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utc_now, onupdate=utc_now, nullable=False
    )


class TherapistAvailability(Base):
    __tablename__ = "therapist_availability"
    __table_args__ = (
        CheckConstraint("weekday >= 0 AND weekday <= 6", name="ck_availability_weekday"),
        CheckConstraint("start_minute >= 0 AND start_minute < end_minute AND end_minute <= 1440", name="ck_availability_minutes"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    availability_id: Mapped[str] = mapped_column(String(36), unique=True, index=True, nullable=False)
    therapist_user_id: Mapped[str] = mapped_column(
        ForeignKey("users.user_id", ondelete="CASCADE"), index=True, nullable=False
    )
    weekday: Mapped[int] = mapped_column(Integer, index=True, nullable=False)
    start_minute: Mapped[int] = mapped_column(Integer, nullable=False)
    end_minute: Mapped[int] = mapped_column(Integer, nullable=False)
    timezone_name: Mapped[str] = mapped_column(String(64), default="Africa/Cairo", nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)


class Appointment(Base):
    __tablename__ = "appointments"
    __table_args__ = (
        CheckConstraint("ends_at > starts_at", name="ck_appointment_time_range"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    appointment_id: Mapped[str] = mapped_column(String(36), unique=True, index=True, nullable=False)
    patient_id: Mapped[str] = mapped_column(
        ForeignKey("patient_profiles.patient_id", ondelete="CASCADE"), index=True, nullable=False
    )
    therapist_user_id: Mapped[str] = mapped_column(
        ForeignKey("users.user_id", ondelete="CASCADE"), index=True, nullable=False
    )
    service_id: Mapped[str | None] = mapped_column(String(36), index=True)
    starts_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True, nullable=False)
    ends_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True, nullable=False)
    status: Mapped[str] = mapped_column(String(24), default="scheduled", index=True, nullable=False)
    delivery_mode: Mapped[str] = mapped_column(String(24), default="video", nullable=False)
    daily_room_name: Mapped[str | None] = mapped_column(String(128), unique=True)
    payment_status: Mapped[str] = mapped_column(String(24), default="unpaid", index=True, nullable=False)
    cancellation_reason: Mapped[str | None] = mapped_column(Text)
    created_by_user_id: Mapped[str] = mapped_column(String(36), index=True, nullable=False)
    idempotency_key: Mapped[str | None] = mapped_column(String(128), unique=True, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utc_now, onupdate=utc_now, nullable=False
    )


class ClinicalSessionNote(Base):
    __tablename__ = "clinical_session_notes"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    note_id: Mapped[str] = mapped_column(String(36), unique=True, index=True, nullable=False)
    appointment_id: Mapped[str] = mapped_column(
        ForeignKey("appointments.appointment_id", ondelete="CASCADE"), index=True, nullable=False
    )
    therapist_user_id: Mapped[str] = mapped_column(String(36), index=True, nullable=False)
    summary: Mapped[str] = mapped_column(Text, nullable=False)
    recommendations: Mapped[str | None] = mapped_column(Text)
    patient_visible: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utc_now, onupdate=utc_now, nullable=False
    )


class Notification(Base):
    __tablename__ = "notifications"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    notification_id: Mapped[str] = mapped_column(String(36), unique=True, index=True, nullable=False)
    user_id: Mapped[str] = mapped_column(
        ForeignKey("users.user_id", ondelete="CASCADE"), index=True, nullable=False
    )
    kind: Mapped[str] = mapped_column(String(64), index=True, nullable=False)
    title: Mapped[str] = mapped_column(String(160), nullable=False)
    body: Mapped[str] = mapped_column(Text, nullable=False)
    action_url: Mapped[str | None] = mapped_column(Text)
    dedup_key: Mapped[str | None] = mapped_column(String(160), unique=True, index=True)
    read_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    email_sent_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    email_required: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    email_attempts: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    next_email_attempt_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), index=True)
    last_email_error: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, index=True, nullable=False)


class ServiceOffering(Base):
    __tablename__ = "service_offerings"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    service_id: Mapped[str] = mapped_column(String(36), unique=True, index=True, nullable=False)
    name_en: Mapped[str] = mapped_column(String(120), nullable=False)
    name_ar: Mapped[str] = mapped_column(String(120), nullable=False)
    description_en: Mapped[str | None] = mapped_column(Text)
    description_ar: Mapped[str | None] = mapped_column(Text)
    duration_minutes: Mapped[int] = mapped_column(Integer, nullable=False)
    price_minor: Mapped[int] = mapped_column(Integer, nullable=False)
    currency: Mapped[str] = mapped_column(String(3), default="EGP", nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, index=True, nullable=False)


class PackageOffering(Base):
    __tablename__ = "package_offerings"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    package_id: Mapped[str] = mapped_column(String(36), unique=True, index=True, nullable=False)
    name_en: Mapped[str] = mapped_column(String(120), nullable=False)
    name_ar: Mapped[str] = mapped_column(String(120), nullable=False)
    sessions_count: Mapped[int] = mapped_column(Integer, nullable=False)
    validity_days: Mapped[int] = mapped_column(Integer, nullable=False)
    price_minor: Mapped[int] = mapped_column(Integer, nullable=False)
    currency: Mapped[str] = mapped_column(String(3), default="EGP", nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, index=True, nullable=False)


class Order(Base):
    __tablename__ = "orders"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    order_id: Mapped[str] = mapped_column(String(36), unique=True, index=True, nullable=False)
    user_id: Mapped[str] = mapped_column(
        ForeignKey("users.user_id", ondelete="RESTRICT"), index=True, nullable=False
    )
    service_id: Mapped[str | None] = mapped_column(String(36), index=True)
    package_id: Mapped[str | None] = mapped_column(String(36), index=True)
    appointment_id: Mapped[str | None] = mapped_column(String(36), index=True)
    amount_minor: Mapped[int] = mapped_column(Integer, nullable=False)
    currency: Mapped[str] = mapped_column(String(3), default="EGP", nullable=False)
    status: Mapped[str] = mapped_column(String(24), default="pending", index=True, nullable=False)
    paymob_order_id: Mapped[str | None] = mapped_column(String(64), unique=True, index=True)
    idempotency_key: Mapped[str] = mapped_column(String(128), unique=True, index=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utc_now, onupdate=utc_now, nullable=False
    )


class Payment(Base):
    __tablename__ = "payments"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    payment_id: Mapped[str] = mapped_column(String(36), unique=True, index=True, nullable=False)
    order_id: Mapped[str] = mapped_column(
        ForeignKey("orders.order_id", ondelete="RESTRICT"), index=True, nullable=False
    )
    provider_transaction_id: Mapped[str] = mapped_column(String(80), unique=True, index=True, nullable=False)
    amount_minor: Mapped[int] = mapped_column(Integer, nullable=False)
    status: Mapped[str] = mapped_column(String(24), index=True, nullable=False)
    provider_payload_json: Mapped[str] = mapped_column(Text, default="{}", nullable=False)
    received_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, nullable=False)


class Refund(Base):
    __tablename__ = "refunds"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    refund_id: Mapped[str] = mapped_column(String(36), unique=True, index=True, nullable=False)
    payment_id: Mapped[str] = mapped_column(
        ForeignKey("payments.payment_id", ondelete="RESTRICT"), index=True, nullable=False
    )
    amount_minor: Mapped[int] = mapped_column(Integer, nullable=False)
    reason: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[str] = mapped_column(String(24), default="pending", index=True, nullable=False)
    requested_by_user_id: Mapped[str] = mapped_column(String(36), index=True, nullable=False)
    provider_refund_id: Mapped[str | None] = mapped_column(String(80), unique=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, nullable=False)


class PlatformSetting(Base):
    __tablename__ = "platform_settings"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    key: Mapped[str] = mapped_column(String(96), unique=True, index=True, nullable=False)
    value_json: Mapped[str] = mapped_column(Text, nullable=False)
    updated_by_user_id: Mapped[str | None] = mapped_column(String(36), index=True)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utc_now, onupdate=utc_now, nullable=False
    )


class ProgressReport(Base):
    __tablename__ = "progress_reports"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    progress_report_id: Mapped[str] = mapped_column(String(36), unique=True, index=True, nullable=False)
    patient_id: Mapped[str] = mapped_column(
        ForeignKey("patient_profiles.patient_id", ondelete="CASCADE"), index=True, nullable=False
    )
    created_by_user_id: Mapped[str] = mapped_column(String(36), index=True, nullable=False)
    artifact_id: Mapped[str] = mapped_column(String(64), unique=True, index=True, nullable=False)
    shared_with_patient: Mapped[bool] = mapped_column(Boolean, default=False, index=True, nullable=False)
    period_start: Mapped[date] = mapped_column(Date, nullable=False)
    period_end: Mapped[date] = mapped_column(Date, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, nullable=False)


class DataRightsRequest(Base):
    __tablename__ = "data_rights_requests"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    request_id: Mapped[str] = mapped_column(String(36), unique=True, index=True, nullable=False)
    user_id: Mapped[str] = mapped_column(ForeignKey("users.user_id", ondelete="CASCADE"), index=True, nullable=False)
    request_type: Mapped[str] = mapped_column(String(24), index=True, nullable=False)
    status: Mapped[str] = mapped_column(String(24), default="pending", index=True, nullable=False)
    details: Mapped[str | None] = mapped_column(Text)
    resolution_note: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, nullable=False)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
