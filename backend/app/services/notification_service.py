"""Durable appointment reminders and retryable email delivery."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone

from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session

from app.db.models import (
    AdherenceEntry,
    Appointment,
    AuditLog,
    Notification,
    PatientProfile,
    TherapistPatientAssignment,
    User,
    utc_now,
)
from app.schemas.auth_schema import UserRole
from app.services.care_service import create_notification
from app.services.email_service import EmailDeliveryError, send_care_notification_email


PASSWORD_RESET_EMAIL_FAILED = "password_reset_email_failed"


def notify_super_admins_of_password_email_failure(
    db: Session,
    user: User,
) -> None:
    """Queue an in-app support alert without exposing the reset token."""
    attempted_at = user.reset_password_sent_at or utc_now()
    super_admins = db.scalars(
        select(User).where(
            User.role == UserRole.super_admin.value,
            User.is_active.is_(True),
            User.account_status == "active",
        ),
    ).all()
    for administrator in super_admins:
        notification = create_notification(
            db,
            administrator.user_id,
            PASSWORD_RESET_EMAIL_FAILED,
            "Password reset email needs attention",
            (
                f"The password reset email for {user.email} could not be delivered. "
                "Verify the user's identity before performing a manual password reset."
            ),
            action_url=f"/admin/users/{user.user_id}",
            dedup_key=(
                f"password-reset-email-failed:{administrator.user_id}:"
                f"{user.user_id}:{attempted_at:%Y%m%d%H%M}"
            ),
        )
        notification.email_required = False

    db.add(
        AuditLog(
            actor_user_id=None,
            action="user.password_reset_email_failed",
            resource_type="user",
            resource_id=user.user_id,
            metadata_json='{"super_admin_notification_created":true}',
        ),
    )


def enqueue_due_appointment_reminders(db: Session, now: datetime | None = None) -> int:
    current = now or datetime.now(timezone.utc)
    created = 0
    windows = ((24, 30), (1, 10))
    for hours, tolerance_minutes in windows:
        target = current + timedelta(hours=hours)
        rows = db.scalars(select(Appointment).where(
            Appointment.status.in_(["scheduled", "confirmed"]),
            Appointment.starts_at >= target - timedelta(minutes=tolerance_minutes),
            Appointment.starts_at <= target + timedelta(minutes=tolerance_minutes),
        )).all()
        for appointment in rows:
            patient = db.scalar(select(PatientProfile).where(PatientProfile.patient_id == appointment.patient_id))
            recipients = [appointment.therapist_user_id]
            if patient and patient.user_id:
                recipients.append(patient.user_id)
            for user_id in recipients:
                dedup = f"appointment:{appointment.appointment_id}:reminder:{hours}h:{user_id}"
                before = db.scalar(select(Notification.id).where(Notification.dedup_key == dedup))
                if before is None:
                    create_notification(
                        db, user_id, "appointment_reminder", "Appointment reminder",
                        f"Your appointment starts in about {hours} hour{'s' if hours != 1 else ''}.",
                        action_url="/appointments", dedup_key=dedup,
                    )
                    created += 1
    db.commit()
    return created


def enqueue_low_adherence_alerts(db: Session, now: datetime | None = None) -> int:
    current = now or datetime.now(timezone.utc)
    cutoff = current.date() - timedelta(days=7)
    rows = db.execute(select(
        AdherenceEntry.patient_id, func.count(AdherenceEntry.id),
    ).where(
        AdherenceEntry.scheduled_date >= cutoff,
        AdherenceEntry.completion_status == "not_completed",
    ).group_by(AdherenceEntry.patient_id).having(func.count(AdherenceEntry.id) >= 3)).all()
    created = 0
    week = current.strftime("%G-W%V")
    for patient_id, missed_count in rows:
        assignments = db.scalars(select(TherapistPatientAssignment).where(
            TherapistPatientAssignment.patient_id == patient_id,
            TherapistPatientAssignment.status == "active",
        )).all()
        for assignment in assignments:
            dedup = f"adherence:{patient_id}:missed:{week}:{assignment.therapist_user_id}"
            if db.scalar(select(Notification.id).where(Notification.dedup_key == dedup)) is None:
                create_notification(
                    db, assignment.therapist_user_id, "low_adherence", "Repeated missed exercises",
                    f"The patient recorded {missed_count} incomplete exercises in the last 7 days.",
                    action_url=f"/therapist/patients/{patient_id}", dedup_key=dedup,
                )
                created += 1
    db.commit()
    return created


def deliver_pending_emails(db: Session, now: datetime | None = None, limit: int = 100) -> tuple[int, int]:
    current = now or datetime.now(timezone.utc)
    rows = db.scalars(select(Notification).where(
        Notification.email_required.is_(True),
        Notification.email_sent_at.is_(None),
        Notification.email_attempts < 5,
        or_(Notification.next_email_attempt_at.is_(None), Notification.next_email_attempt_at <= current),
    ).order_by(Notification.created_at.asc()).limit(limit)).all()
    sent = failed = 0
    for row in rows:
        user = db.scalar(select(User).where(User.user_id == row.user_id))
        if user is None or not user.email:
            row.email_required = False
            continue
        try:
            send_care_notification_email(user.email, row.title, row.body, row.action_url)
            row.email_sent_at = current
            row.last_email_error = None
            sent += 1
        except EmailDeliveryError as exc:
            row.email_attempts += 1
            row.last_email_error = str(exc)[:500]
            row.next_email_attempt_at = current + timedelta(minutes=2 ** row.email_attempts)
            failed += 1
    db.commit()
    return sent, failed
