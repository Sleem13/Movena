"""Therapist care operations beyond the analysis prototype."""

import json
from datetime import date, datetime, timedelta, timezone
from uuid import uuid4

from fastapi import APIRouter, Depends, Query, status
from fastapi.responses import JSONResponse
from sqlalchemy import or_, select
from sqlalchemy.orm import Session

from app.api.dependencies.auth import require_therapist
from app.api.error_responses import api_error_response
from app.db.database import get_db
from app.db.models import (
    AdherenceEntry, Appointment, ClinicalSessionNote, Notification, PatientProfile,
    ProgressReport, TherapistAvailability, User,
)
from app.schemas.care_schema import (
    AppointmentSummary, ClinicalNoteCreate, ClinicalNoteDetail, NotificationSummary,
    AvailabilityCreate, AvailabilityDetail, ExerciseResponseReview,
)
from app.services.artifact_service import build_artifact_url, create_artifact
from app.services.care_service import (
    acknowledge_exercise_response, appointment_summary, audit_event,
    notification_summary, user_can_access_patient,
)
from app.services.progress_report_service import generate_progress_report
from app.services.notification_service import notification_accessible

router = APIRouter(
    prefix="/api/v1/therapist", tags=["therapist-care"],
    dependencies=[Depends(require_therapist)],
)


@router.post("/availability", response_model=AvailabilityDetail, status_code=status.HTTP_201_CREATED)
def add_availability(
    data: AvailabilityCreate, actor: User = Depends(require_therapist),
    db: Session = Depends(get_db),
):
    row = TherapistAvailability(
        availability_id=str(uuid4()), therapist_user_id=actor.user_id,
        weekday=data.weekday, start_minute=data.start_minute, end_minute=data.end_minute,
        timezone_name=data.timezone_name, is_active=True,
    )
    db.add(row)
    audit_event(db, actor.user_id, "availability.created", "availability", row.availability_id, data.model_dump())
    db.commit(); db.refresh(row)
    return row


@router.get("/availability", response_model=list[AvailabilityDetail])
def list_availability(actor: User = Depends(require_therapist), db: Session = Depends(get_db)):
    return list(db.scalars(select(TherapistAvailability).where(
        TherapistAvailability.therapist_user_id == actor.user_id,
        TherapistAvailability.is_active.is_(True),
    ).order_by(TherapistAvailability.weekday, TherapistAvailability.start_minute)).all())


def error(code: str, message: str, status_code: int) -> JSONResponse:
    return api_error_response(code, message, status_code)


@router.get("/appointments", response_model=list[AppointmentSummary])
def appointments(actor: User = Depends(require_therapist), db: Session = Depends(get_db)):
    statement = select(Appointment)
    if actor.role == "therapist":
        statement = statement.where(Appointment.therapist_user_id == actor.user_id)
    rows = db.scalars(statement.order_by(Appointment.starts_at.desc()).limit(200)).all()
    return [appointment_summary(row) for row in rows if user_can_access_patient(db, actor, row.patient_id)]


@router.get("/adherence-alerts", response_model=list[NotificationSummary])
def adherence_alerts(actor: User = Depends(require_therapist), db: Session = Depends(get_db)):
    rows = db.scalars(select(Notification).where(
        Notification.user_id == actor.user_id,
        Notification.kind.in_(["high_pain", "low_adherence", "exercise_response_follow_up"]),
    ).order_by(Notification.created_at.desc()).limit(100)).all()
    return [notification_summary(row) for row in rows if notification_accessible(db, row, actor)]


@router.get("/patients/{patient_id}/adherence")
def patient_adherence(
    patient_id: str, start: date | None = Query(None), end: date | None = Query(None),
    actor: User = Depends(require_therapist), db: Session = Depends(get_db),
):
    if not user_can_access_patient(db, actor, patient_id):
        return error("PATIENT_ACCESS_DENIED", "This patient is not assigned to you.", 403)
    statement = select(AdherenceEntry).where(AdherenceEntry.patient_id == patient_id)
    if start:
        statement = statement.where(AdherenceEntry.scheduled_date >= start)
    if end:
        statement = statement.where(AdherenceEntry.scheduled_date <= end)
    rows = db.scalars(statement.order_by(AdherenceEntry.scheduled_date.desc()).limit(365)).all()
    return [{
        "adherence_id": row.adherence_id, "plan_item_id": row.plan_item_id,
        "scheduled_date": row.scheduled_date, "completion_status": row.completion_status,
        "pain_before": row.pain_before, "pain_after": row.pain_after,
        "difficulty": row.difficulty, "fatigue": row.fatigue, "note": row.note,
        "perceived_exertion": row.perceived_exertion,
        "symptoms_changed": row.symptoms_changed,
        "stopped_due_to_symptoms": row.stopped_due_to_symptoms,
        "symptom_flags": json.loads(row.symptom_flags_json or "[]"),
        "response_state": row.response_state,
        "supportive_instruction": row.supportive_instruction,
        "clinician_review_required": row.clinician_review_required,
        "reviewed_at": row.reviewed_at,
        "reviewed_by_user_id": row.reviewed_by_user_id,
        "reviewed_by_name": db.scalar(select(User.full_name).where(User.user_id == row.reviewed_by_user_id)) if row.reviewed_by_user_id else None,
        "review_disposition": row.review_disposition,
        "review_note": row.review_note,
        "analysis_session_id": row.analysis_session_id,
    } for row in rows]


@router.post("/patients/{patient_id}/adherence/{adherence_id}/acknowledge")
def acknowledge_adherence_response(
    patient_id: str, adherence_id: str, data: ExerciseResponseReview,
    actor: User = Depends(require_therapist), db: Session = Depends(get_db),
):
    if not user_can_access_patient(db, actor, patient_id):
        return error("PATIENT_ACCESS_DENIED", "This patient is not assigned to you.", 403)
    row = db.scalar(select(AdherenceEntry).where(
        AdherenceEntry.adherence_id == adherence_id,
        AdherenceEntry.patient_id == patient_id,
    ))
    if row is None:
        return error("ADHERENCE_NOT_FOUND", "Exercise response was not found.", 404)
    try:
        reviewed = acknowledge_exercise_response(db, actor, row, data)
    except ValueError:
        return error("REVIEW_NOT_REQUIRED", "This exercise response does not require review.", 409)
    return {
        "adherence_id": reviewed.adherence_id,
        "response_state": reviewed.response_state,
        "clinician_review_required": reviewed.clinician_review_required,
        "reviewed_at": reviewed.reviewed_at,
        "reviewed_by_user_id": reviewed.reviewed_by_user_id,
        "review_disposition": reviewed.review_disposition,
        "review_note": reviewed.review_note,
    }


@router.post(
    "/appointments/{appointment_id}/session-notes",
    response_model=ClinicalNoteDetail, status_code=status.HTTP_201_CREATED,
)
def create_session_note(
    appointment_id: str, data: ClinicalNoteCreate,
    actor: User = Depends(require_therapist), db: Session = Depends(get_db),
):
    appointment = db.scalar(select(Appointment).where(Appointment.appointment_id == appointment_id))
    if appointment is None:
        return error("APPOINTMENT_NOT_FOUND", "Appointment was not found.", 404)
    if not user_can_access_patient(db, actor, appointment.patient_id):
        return error("PATIENT_ACCESS_DENIED", "An active care connection is required.", 403)
    if actor.role == "therapist" and appointment.therapist_user_id != actor.user_id:
        return error("APPOINTMENT_ACCESS_DENIED", "This appointment is not assigned to you.", 403)
    row = ClinicalSessionNote(
        note_id=str(uuid4()), appointment_id=appointment_id,
        therapist_user_id=actor.user_id, **data.model_dump(),
    )
    db.add(row)
    audit_event(db, actor.user_id, "session_note.created", "appointment", appointment_id, {
        "patient_visible": data.patient_visible,
    })
    db.commit(); db.refresh(row)
    return row


@router.post("/patients/{patient_id}/reports")
def create_progress_report(
    patient_id: str, period_start: date, period_end: date,
    share_with_patient: bool = False,
    actor: User = Depends(require_therapist), db: Session = Depends(get_db),
):
    if period_end < period_start or period_end - period_start > timedelta(days=366):
        return error("INVALID_REPORT_PERIOD", "Choose a report period of up to one year.", 422)
    if not user_can_access_patient(db, actor, patient_id):
        return error("PATIENT_ACCESS_DENIED", "This patient is not assigned to you.", 403)
    patient = db.scalar(select(PatientProfile).where(PatientProfile.patient_id == patient_id))
    if patient is None:
        return error("PATIENT_NOT_FOUND", "Patient profile was not found.", 404)
    artifact_id, path = create_artifact("report")
    generate_progress_report(db, patient, period_start, period_end, path)
    report = ProgressReport(
        progress_report_id=str(uuid4()), patient_id=patient_id,
        created_by_user_id=actor.user_id, artifact_id=artifact_id,
        shared_with_patient=share_with_patient,
        period_start=period_start, period_end=period_end,
    )
    db.add(report)
    audit_event(db, actor.user_id, "progress_report.created", "progress_report", report.progress_report_id, {
        "patient_id": patient_id, "shared_with_patient": share_with_patient,
    })
    db.commit()
    return {
        "progress_report_id": report.progress_report_id,
        "download_url": build_artifact_url(
            f"/api/v1/artifacts/reports/{artifact_id}", artifact_id, "report", exercise_id="progress"
        ),
        "shared_with_patient": share_with_patient,
    }
