"""Durable appointment reminders and retryable email delivery."""

from __future__ import annotations

from datetime import datetime, time, timedelta, timezone
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session

from app.db.models import (
    AdherenceEntry,
    Appointment,
    AuditLog,
    Notification,
    PatientProfile,
    RecoveryCoachingCheckIn,
    RecoveryCoachingReminderPreference,
    TherapistPatientAssignment,
    User,
    utc_now,
)
from app.schemas.auth_schema import UserRole
from app.services.care_service import create_notification, therapist_can_access_patient


def notification_accessible(db, row, user):
    if user.role != "therapist":
        return True
    path = (row.action_url or "").split("?")[0].split("/")
    if len(path) >= 4 and path[1:3] == ["therapist", "patients"]:
        return therapist_can_access_patient(db, user.user_id, path[3])
    if (row.dedup_key or "").startswith("appointment:"):
        appointment_id = row.dedup_key.split(":")[1]
        appointment = db.scalar(select(Appointment).where(Appointment.appointment_id == appointment_id))
        return bool(appointment and therapist_can_access_patient(db, user.user_id, appointment.patient_id))
    return True
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
            if not therapist_can_access_patient(db, appointment.therapist_user_id, appointment.patient_id):
                continue
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


def enqueue_recovery_coaching_reminders(
    db: Session, now: datetime | None = None,
) -> tuple[int, int]:
    """Queue opt-in patient reminders and non-urgent missed-check-in follow-up.

    This worker is periodic and does not promise real-time monitoring or a
    guaranteed clinical response time.
    """
    current = now or datetime.now(timezone.utc)
    patient_reminders = therapist_follow_ups = 0
    preferences = db.scalars(select(RecoveryCoachingReminderPreference).where(
        RecoveryCoachingReminderPreference.enabled.is_(True),
        RecoveryCoachingReminderPreference.patient_agreed.is_(True),
    )).all()
    for preference in preferences:
        patient = db.scalar(select(PatientProfile).where(
            PatientProfile.patient_id == preference.patient_id,
        ))
        if patient is None or not patient.user_id:
            continue
        try:
            local_zone = ZoneInfo(patient.timezone_name or "UTC")
        except ZoneInfoNotFoundError:
            local_zone = timezone.utc
        local_now = current.astimezone(local_zone)
        if preference.cadence == "weekdays" and local_now.weekday() >= 5:
            continue
        try:
            reminder_time = time.fromisoformat(preference.local_time)
        except ValueError:
            reminder_time = time(19, 0)
        due_at = datetime.combine(local_now.date(), reminder_time, tzinfo=local_zone)
        if local_now < due_at:
            continue

        checked_in = db.scalar(select(RecoveryCoachingCheckIn.id).where(
            RecoveryCoachingCheckIn.patient_id == patient.patient_id,
            RecoveryCoachingCheckIn.check_in_date == local_now.date(),
        )) is not None
        if not checked_in:
            dedup = f"recovery-checkin-reminder:{patient.patient_id}:{local_now.date().isoformat()}"
            if db.scalar(select(Notification.id).where(Notification.dedup_key == dedup)) is None:
                create_notification(
                    db, patient.user_id, "recovery_coaching_reminder",
                    "Recovery check-in reminder",
                    "If it is appropriate and safe, record today's brief recovery reflection. This is not monitored in real time.",
                    action_url="/recovery-coaching", dedup_key=dedup,
                )
                patient_reminders += 1

        last_check_in = db.scalar(select(func.max(RecoveryCoachingCheckIn.check_in_date)).where(
            RecoveryCoachingCheckIn.patient_id == patient.patient_id,
        ))
        preference_start = preference.created_at.astimezone(local_zone).date() if preference.created_at.tzinfo else preference.created_at.date()
        reference_date = last_check_in or preference_start
        days_since = (local_now.date() - reference_date).days
        if checked_in or days_since < preference.missed_follow_up_days:
            continue
        assignments = db.scalars(select(TherapistPatientAssignment).where(
            TherapistPatientAssignment.patient_id == patient.patient_id,
            TherapistPatientAssignment.status == "active",
        )).all()
        period = local_now.strftime("%G-W%V")
        for assignment in assignments:
            dedup = f"recovery-checkin-missed:{patient.patient_id}:{period}:{assignment.therapist_user_id}"
            if db.scalar(select(Notification.id).where(Notification.dedup_key == dedup)) is None:
                create_notification(
                    db, assignment.therapist_user_id, "recovery_coaching_missed_check_in",
                    "Recovery coaching follow-up",
                    f"{patient.display_name} has not recorded a coaching check-in for {days_since} days. This is a routine follow-up signal, not real-time monitoring.",
                    action_url="/recovery-coaching", dedup_key=dedup,
                )
                therapist_follow_ups += 1
    db.commit()
    return patient_reminders, therapist_follow_ups


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
        if not user.is_active or user.account_status != "active" or not notification_accessible(db, row, user):
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
