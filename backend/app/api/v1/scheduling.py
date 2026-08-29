"""Appointment scheduling and secure join APIs."""

from datetime import date, datetime, timedelta, timezone
from zoneinfo import ZoneInfo

from fastapi import APIRouter, Depends, Header, Query, status
from fastapi.responses import JSONResponse
from sqlalchemy import select, text
from sqlalchemy.orm import Session

from app.api.dependencies.auth import get_current_user, require_patient_or_therapist
from app.api.error_responses import api_error_response
from app.db.database import get_db
from app.core.config import get_settings
from app.db.models import Appointment, PatientProfile, TherapistAvailability, User
from app.schemas.care_schema import (
    AppointmentCreate, AppointmentJoinResponse, AppointmentSummary, AppointmentUpdate,
)
from app.services.care_service import (
    appointment_summary, create_appointment, patient_for_user,
    therapist_can_access_patient, user_can_access_patient, audit_event, create_notification,
)
from app.services.telemedicine_service import TelemedicineError, create_join_token

router = APIRouter(prefix="/api/v1/scheduling", tags=["scheduling"])


def error(code: str, message: str, status_code: int) -> JSONResponse:
    return api_error_response(code, message, status_code)


@router.get("/availability")
def availability(
    therapist_user_id: str, day: date = Query(), db: Session = Depends(get_db),
):
    rows = db.scalars(select(TherapistAvailability).where(
        TherapistAvailability.therapist_user_id == therapist_user_id,
        TherapistAvailability.weekday == day.weekday(),
        TherapistAvailability.is_active.is_(True),
    )).all()
    slots = []
    for row in rows:
        local_tz = ZoneInfo(row.timezone_name)
        local_start = datetime.combine(day, datetime.min.time(), tzinfo=local_tz) + timedelta(minutes=row.start_minute)
        local_end = datetime.combine(day, datetime.min.time(), tzinfo=local_tz) + timedelta(minutes=row.end_minute)
        cursor = local_start.astimezone(timezone.utc)
        end = local_end.astimezone(timezone.utc)
        while cursor + timedelta(minutes=30) <= end:
            slot_end = cursor + timedelta(minutes=30)
            conflict = db.scalar(select(Appointment.id).where(
                Appointment.therapist_user_id == therapist_user_id,
                Appointment.status.in_(["scheduled", "confirmed"]),
                Appointment.starts_at < slot_end, Appointment.ends_at > cursor,
            ))
            if conflict is None:
                slots.append({"starts_at": cursor, "ends_at": slot_end})
            cursor = slot_end
    return {"therapist_user_id": therapist_user_id, "date": day, "slots": slots}


@router.post("/appointments", response_model=AppointmentSummary, status_code=status.HTTP_201_CREATED)
def book(
    data: AppointmentCreate,
    idempotency_key: str | None = Header(default=None, alias="Idempotency-Key", max_length=128),
    actor: User = Depends(require_patient_or_therapist), db: Session = Depends(get_db),
):
    if actor.role == "patient":
        profile = patient_for_user(db, actor.user_id)
        if profile is None or profile.patient_id != data.patient_id:
            return error("PATIENT_ACCESS_DENIED", "You can only book your own appointments.", 403)
        if not therapist_can_access_patient(db, data.therapist_user_id, data.patient_id):
            return error("THERAPIST_NOT_ASSIGNED", "Choose a therapist assigned to your care.", 403)
    elif actor.role == "therapist" and not therapist_can_access_patient(db, actor.user_id, data.patient_id):
        return error("PATIENT_ACCESS_DENIED", "This patient is not assigned to you.", 403)
    if db.scalar(select(PatientProfile.patient_id).where(PatientProfile.patient_id == data.patient_id)) is None:
        return error("PATIENT_NOT_FOUND", "Patient profile was not found.", 404)
    try:
        row = create_appointment(db, data, actor.user_id, idempotency_key)
    except ValueError:
        return error("APPOINTMENT_CONFLICT", "The therapist already has an appointment in this time range.", 409)
    return appointment_summary(row)


@router.get("/appointments/{appointment_id}/join", response_model=AppointmentJoinResponse)
def join(
    appointment_id: str, actor: User = Depends(get_current_user), db: Session = Depends(get_db),
):
    row = db.scalar(select(Appointment).where(Appointment.appointment_id == appointment_id))
    if row is None:
        return error("APPOINTMENT_NOT_FOUND", "Appointment was not found.", 404)
    is_therapist = actor.user_id == row.therapist_user_id
    if not is_therapist and not user_can_access_patient(db, actor, row.patient_id):
        return error("APPOINTMENT_ACCESS_DENIED", "You cannot join this appointment.", 403)
    if row.status not in {"scheduled", "confirmed"}:
        return error("APPOINTMENT_NOT_JOINABLE", "This appointment cannot be joined.", 409)
    try:
        room_url, token, expires_at = create_join_token(row, actor, is_owner=is_therapist)
    except TelemedicineError as exc:
        return error("VIDEO_SESSION_UNAVAILABLE", str(exc), 409)
    db.commit()
    return AppointmentJoinResponse(
        appointment_id=row.appointment_id, room_url=room_url,
        meeting_token=token, expires_at=expires_at,
    )


@router.patch("/appointments/{appointment_id}", response_model=AppointmentSummary)
def update_appointment(
    appointment_id: str, data: AppointmentUpdate,
    actor: User = Depends(get_current_user), db: Session = Depends(get_db),
):
    row = db.scalar(select(Appointment).where(
        Appointment.appointment_id == appointment_id
    ).with_for_update())
    if row is None:
        return error("APPOINTMENT_NOT_FOUND", "Appointment was not found.", 404)
    is_therapist = actor.user_id == row.therapist_user_id
    if not is_therapist and not user_can_access_patient(db, actor, row.patient_id):
        return error("APPOINTMENT_ACCESS_DENIED", "You cannot change this appointment.", 403)
    if data.status == "cancelled" and actor.role == "patient":
        starts = row.starts_at if row.starts_at.tzinfo else row.starts_at.replace(tzinfo=timezone.utc)
        if datetime.now(timezone.utc) > starts - timedelta(hours=get_settings().cancellation_window_hours):
            return error("CANCELLATION_WINDOW_CLOSED", "Contact the clinic to cancel within 24 hours of the appointment.", 409)
    if data.starts_at:
        starts = data.starts_at.astimezone(timezone.utc)
        ends = data.ends_at.astimezone(timezone.utc)
        if db.bind is not None and db.bind.dialect.name == "postgresql":
            db.execute(text("SELECT pg_advisory_xact_lock(hashtext(:therapist_id))"), {
                "therapist_id": row.therapist_user_id,
            })
        conflict = db.scalar(select(Appointment.id).where(
            Appointment.therapist_user_id == row.therapist_user_id,
            Appointment.appointment_id != row.appointment_id,
            Appointment.status.in_(["scheduled", "confirmed"]),
            Appointment.starts_at < ends, Appointment.ends_at > starts,
        ))
        if conflict is not None:
            return error("APPOINTMENT_CONFLICT", "The therapist already has an appointment in this time range.", 409)
        row.starts_at, row.ends_at = starts, ends
        row.daily_room_name = None
    if data.status:
        row.status = data.status
    if data.cancellation_reason:
        row.cancellation_reason = data.cancellation_reason
    patient = db.scalar(select(PatientProfile).where(PatientProfile.patient_id == row.patient_id))
    recipient_ids = {row.therapist_user_id}
    if patient and patient.user_id:
        recipient_ids.add(patient.user_id)
    for user_id in recipient_ids - {actor.user_id}:
        create_notification(
            db, user_id, "appointment_updated", "Appointment updated",
            f"Appointment {row.appointment_id} has been updated.", action_url="/appointments",
            dedup_key=f"appointment:{row.appointment_id}:updated:{row.updated_at.timestamp()}:{user_id}",
        )
    audit_event(db, actor.user_id, "appointment.updated", "appointment", row.appointment_id, data.model_dump(exclude_none=True, mode="json"))
    db.commit(); db.refresh(row)
    return appointment_summary(row)
