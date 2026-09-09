"""Transactional care connections. Callers commit the complete lifecycle event."""
import hashlib
import secrets
from datetime import datetime, timedelta, timezone
from uuid import uuid4

from sqlalchemy import func, select, text
from sqlalchemy.orm import Session

from app.api.dependencies.auth import AuthError
from app.db.models import CareInvitation, PatientProfile, TherapistPatientAssignment, User, Appointment
from app.services.care_service import audit_event, create_notification, ensure_assignment
from app.services.email_service import EmailDeliveryError, send_care_notification_email


def fail(message, code="CONNECTION_INVALID", status=409):
    raise AuthError(status, code, message)


def now():
    return datetime.now(timezone.utc)


def aware(value):
    return value if value.tzinfo else value.replace(tzinfo=timezone.utc)


def lock_therapist(db, user_id):
    # A write lock also serializes SQLite transactions before their first read.
    db.execute(text("UPDATE users SET user_id = user_id WHERE user_id = :id"), {"id": user_id})


def active_user(db, user_id, role):
    user = db.scalar(select(User).where(User.user_id == user_id).execution_options(populate_existing=True))
    if not user or user.role != role or not user.is_active or user.account_status != "active":
        fail("The account is not available for this connection.")
    return user


def summary(db, row):
    therapist = db.scalar(select(User).where(User.user_id == row.therapist_user_id))
    patient = db.scalar(select(PatientProfile).where(PatientProfile.patient_id == row.patient_id))
    return {
        "assignment_id": row.assignment_id, "therapist_user_id": row.therapist_user_id,
        "patient_id": row.patient_id, "therapist_name": therapist.full_name or therapist.email,
        "patient_name": patient.display_name, "status": row.status, "source": row.source,
        "assigned_at": row.assigned_at, "ended_at": row.ended_at,
        "appointments_needing_review": db.scalar(select(func.count()).select_from(Appointment).where(
            Appointment.patient_id == row.patient_id, Appointment.therapist_user_id == row.therapist_user_id,
            Appointment.status.in_(["scheduled", "confirmed"]), Appointment.ends_at > now(),
        )) if row.status == "ended" else 0,
    }


def invitation_summary(db, row):
    therapist = db.scalar(select(User).where(User.user_id == row.therapist_user_id))
    return {
        "invitation_id": row.invitation_id, "email": row.email,
        "therapist_name": therapist.full_name or therapist.email,
        "status": "expired" if row.status == "pending" and aware(row.expires_at) <= now() else row.status,
        "expires_at": row.expires_at, "delivery_status": row.delivery_status,
    }


def activate(db, therapist_id, patient_id, actor, source, reason=None):
    lock_therapist(db, therapist_id)
    active_user(db, therapist_id, "therapist")
    patient = db.scalar(select(PatientProfile).where(PatientProfile.patient_id == patient_id))
    if not patient:
        fail("Patient profile was not found.", status=404)
    if patient.user_id:
        active_user(db, patient.user_id, "patient")
    existing = db.scalar(select(TherapistPatientAssignment).where(
        TherapistPatientAssignment.therapist_user_id == therapist_id,
        TherapistPatientAssignment.patient_id == patient_id,
    ).execution_options(populate_existing=True))
    if existing and existing.status == "active":
        return existing
    row = ensure_assignment(db, therapist_id, patient_id, actor.user_id)
    row.source, row.assigned_at = source, now()
    row.ended_at = row.ended_by_user_id = row.end_reason = None
    db.flush()
    audit_event(db, actor.user_id, "connection.activated", "assignment", row.assignment_id,
                {"source": source, "reason": reason, "therapist_user_id": therapist_id, "patient_id": patient_id})
    for uid in {therapist_id, patient.user_id} - {None}:
        create_notification(db, uid, "connection_activated", "Care connection active",
                            "Your care team connection is now active.", "/care-team")
    return row


def invite(db, actor, email, patient_id=None, resend_id=None):
    lock_therapist(db, actor.user_id)
    active_user(db, actor.user_id, "therapist")
    email = email.strip().lower()
    row = db.scalar(select(CareInvitation).where(
        CareInvitation.therapist_user_id == actor.user_id, CareInvitation.email == email,
    ).execution_options(populate_existing=True))
    if resend_id and (not row or row.invitation_id != resend_id):
        fail("Invitation was not found.", status=404)
    if row and row.status == "pending" and aware(row.expires_at) > now() and not resend_id:
        return row, None
    if patient_id:
        profile = db.scalar(select(PatientProfile).where(PatientProfile.patient_id == patient_id))
        assignment = db.scalar(select(TherapistPatientAssignment).where(
            TherapistPatientAssignment.patient_id == patient_id,
            TherapistPatientAssignment.therapist_user_id == actor.user_id,
            TherapistPatientAssignment.status == "active",
        ))
        if not profile or not assignment:
            fail("Only an assigned profile can be linked to an invitation.", status=403)
        if profile.user_id:
            target = active_user(db, profile.user_id, "patient")
            if target.email.lower() != email:
                fail("The invitation email must match the linked patient.")
    token = secrets.token_urlsafe(32)
    if not row:
        row = CareInvitation(invitation_id=str(uuid4()), therapist_user_id=actor.user_id, email=email)
        db.add(row)
    row.patient_id = patient_id if not resend_id else row.patient_id
    row.token_hash = hashlib.sha256(token.encode()).hexdigest()
    row.expires_at, row.status, row.delivery_status = now() + timedelta(days=7), "pending", "pending"
    row.updated_at = now()
    db.flush()
    audit_event(db, actor.user_id, "connection.invited", "invitation", row.invitation_id)
    recipient = db.scalar(select(User).where(func.lower(User.email) == email, User.role == "patient"))
    if recipient:
        note = create_notification(db, recipient.user_id, "care_invitation", "Care invitation",
                                   "A therapist has invited you to connect. Review the invitation in My care team.", "/care-team")
        note.email_required = False
    return row, token


def deliver_invitation(db, row, token):
    if not token:
        return
    try:
        send_care_notification_email(row.email, "Movena care invitation",
            "A therapist has invited you to connect. Sign in with this email to review what will be shared. This invitation expires in seven days.",
            f"/care-team#invitation={token}")
        row.delivery_status = "sent"
    except EmailDeliveryError:
        row.delivery_status = "failed"
    db.commit()


def respond(db, actor, invitation_id, action, token=None):
    active_user(db, actor.user_id, "patient")
    if not actor.is_verified:
        fail("Verify your email before responding to an invitation.", "EMAIL_NOT_VERIFIED", 403)
    row = db.scalar(select(CareInvitation).where(CareInvitation.invitation_id == invitation_id))
    if not row:
        fail("Invitation was not found.", status=404)
    lock_therapist(db, row.therapist_user_id)
    db.refresh(row)
    if row.email != actor.email.strip().lower():
        fail("Sign in with the invited email address.", status=403)
    if token and row.token_hash != hashlib.sha256(token.encode()).hexdigest():
        fail("This invitation link is no longer valid.")
    if row.status != "pending" or aware(row.expires_at) <= now():
        fail("This invitation is no longer pending.")
    if action == "accept":
        active_user(db, row.therapist_user_id, "therapist")
        profile = db.scalar(select(PatientProfile).where(PatientProfile.user_id == actor.user_id))
        if row.patient_id and (not profile or profile.patient_id != row.patient_id):
            # Never merge an existing account's clinical history implicitly.
            fail("Ask an administrator to review the existing patient profile before linking this account.")
        if not profile:
            profile = PatientProfile(patient_id=str(uuid4()), user_id=actor.user_id,
                                     display_name=actor.full_name or actor.email)
            db.add(profile)
            db.flush()
        activate(db, row.therapist_user_id, profile.patient_id, actor, "invitation")
    row.status, row.token_hash = ("accepted" if action == "accept" else "declined"), None
    audit_event(db, actor.user_id, f"connection.{row.status}", "invitation", row.invitation_id)
    return row


def end_connection(db, actor, assignment_id, reason):
    row = db.scalar(select(TherapistPatientAssignment).where(TherapistPatientAssignment.assignment_id == assignment_id))
    if not row:
        fail("Connection was not found.", status=404)
    lock_therapist(db, row.therapist_user_id)
    db.refresh(row)
    patient = db.scalar(select(PatientProfile).where(PatientProfile.patient_id == row.patient_id))
    admin = actor.role in {"admin", "super_admin"}
    participant = (actor.role == "therapist" and actor.user_id == row.therapist_user_id) or (
        actor.role == "patient" and actor.user_id == patient.user_id)
    if not admin and not participant:
        fail("You cannot end this connection.", status=403)
    if admin and not reason:
        fail("An administrative reason is required.", status=422)
    if row.status == "ended":
        return row
    row.status, row.ended_at, row.ended_by_user_id, row.end_reason = "ended", now(), actor.user_id, reason
    if patient.user_id:
        patient_user = db.scalar(select(User).where(User.user_id == patient.user_id))
        for invitation in db.scalars(select(CareInvitation).where(
            CareInvitation.therapist_user_id == row.therapist_user_id,
            CareInvitation.email == patient_user.email.lower(), CareInvitation.status == "pending",
        )):
            invitation.status, invitation.token_hash = "cancelled", None
    db.flush()
    audit_event(db, actor.user_id, "connection.ended", "assignment", row.assignment_id,
                {"reason": reason, "patient_id": row.patient_id, "therapist_user_id": row.therapist_user_id})
    for uid in {row.therapist_user_id, patient.user_id} - {None}:
        create_notification(db, uid, "connection_ended", "Care connection ended",
                            "The therapist no longer has access. Existing patient records are retained.", "/care-team")
    pending = db.scalars(select(Appointment).where(
        Appointment.therapist_user_id == row.therapist_user_id, Appointment.patient_id == row.patient_id,
        Appointment.status.in_(["scheduled", "confirmed"]), Appointment.ends_at > now(),
    )).all()
    if pending:
        for admin_user in db.scalars(select(User).where(User.role.in_(["admin", "super_admin"]), User.is_active.is_(True))):
            create_notification(db, admin_user.user_id, "connection_appointment_review", "Appointments need review",
                                f"{len(pending)} appointments need review after a care connection ended.", "/admin/assignments")
        audit_event(db, actor.user_id, "connection.appointments_need_review", "assignment", row.assignment_id,
                    {"appointment_ids": [a.appointment_id for a in pending]})
    return row
