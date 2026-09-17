"""Patient-owned care workflow APIs."""

from datetime import date, datetime, timezone

from fastapi import APIRouter, Depends, Header, Query, status
from fastapi.responses import JSONResponse
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.dependencies.auth import require_role
from app.api.error_responses import api_error_response
from app.db.database import get_db
from app.db.models import (
    Appointment, DataRightsRequest, Notification, PatientHealthProfile, PatientProfile, ProgressReport,
    User, UserConsent, utc_now,
)
from app.services.artifact_service import build_artifact_url
from app.services.clinical_note_service import appointment_notes
from app.schemas.auth_schema import UserRole
from app.schemas.care_schema import (
    AdherenceCreate, AdherenceDetail, AppointmentSummary, NotificationSummary,
    PatientTodayResponse, PatientHealthProfileUpdate, ConsentUpdate, DataRightsRequestCreate, ClinicalNoteDetail,
)
from app.services.care_service import (
    appointment_summary, audit_event, ensure_patient_profile, notification_summary, patient_today,
    record_adherence,
)

router = APIRouter(
    prefix="/api/v1/patient", tags=["patient"],
    dependencies=[Depends(require_role(UserRole.patient))],
)


def error(code: str, message: str, status_code: int) -> JSONResponse:
    return api_error_response(code, message, status_code)


def current_profile(db: Session, user: User) -> PatientProfile | JSONResponse:
    profile, created = ensure_patient_profile(db, user)
    if created:
        audit_event(db, user.user_id, "patient.profile_repaired", "patient_profile", profile.patient_id)
        db.commit()
        db.refresh(profile)
    return profile


@router.get("/health-profile")
def health_profile(actor: User = Depends(require_role(UserRole.patient)), db: Session = Depends(get_db)):
    profile = current_profile(db, actor)
    if isinstance(profile, JSONResponse):
        return profile
    row = db.scalar(select(PatientHealthProfile).where(PatientHealthProfile.patient_id == profile.patient_id))
    return {
        "patient_id": profile.patient_id,
        "emergency_contact_name": row.emergency_contact_name if row else None,
        "emergency_contact_phone": row.emergency_contact_phone if row else None,
        "medical_summary": row.medical_summary if row else None,
        "precautions": row.precautions if row else None,
    }


@router.patch("/health-profile")
def update_health_profile(
    data: PatientHealthProfileUpdate, actor: User = Depends(require_role(UserRole.patient)),
    db: Session = Depends(get_db),
):
    profile = current_profile(db, actor)
    if isinstance(profile, JSONResponse):
        return profile
    row = db.scalar(select(PatientHealthProfile).where(PatientHealthProfile.patient_id == profile.patient_id))
    if row is None:
        row = PatientHealthProfile(patient_id=profile.patient_id)
        db.add(row)
    for name, value in data.model_dump(exclude_unset=True).items():
        setattr(row, name, value)
    db.commit()
    return health_profile(actor, db)


@router.get("/consents")
def consents(actor: User = Depends(require_role(UserRole.patient)), db: Session = Depends(get_db)):
    rows = db.scalars(select(UserConsent).where(UserConsent.user_id == actor.user_id)).all()
    return [{
        "consent_type": row.consent_type, "accepted": row.accepted,
        "accepted_at": row.accepted_at, "version": row.version,
    } for row in rows]


@router.post("/consents")
def update_consent(
    data: ConsentUpdate, actor: User = Depends(require_role(UserRole.patient)),
    db: Session = Depends(get_db),
):
    row = db.scalar(select(UserConsent).where(
        UserConsent.user_id == actor.user_id, UserConsent.consent_type == data.consent_type,
    ).order_by(UserConsent.id.desc()))
    if row is None or row.version != data.version:
        row = UserConsent(
            user_id=actor.user_id, consent_type=data.consent_type,
            accepted=data.accepted, version=data.version,
        )
        db.add(row)
    else:
        row.accepted = data.accepted
    row.accepted_at = utc_now() if data.accepted else None
    db.commit()
    return {"status": "success", "consent_type": row.consent_type, "accepted": row.accepted}


@router.get("/data-rights-requests")
def data_rights_requests(actor: User = Depends(require_role(UserRole.patient)), db: Session = Depends(get_db)):
    rows = db.scalars(select(DataRightsRequest).where(
        DataRightsRequest.user_id == actor.user_id,
    ).order_by(DataRightsRequest.created_at.desc())).all()
    return [{
        "request_id": row.request_id, "request_type": row.request_type,
        "status": row.status, "details": row.details,
        "created_at": row.created_at, "completed_at": row.completed_at,
    } for row in rows]


@router.post("/data-rights-requests", status_code=status.HTTP_201_CREATED)
def create_data_rights_request(
    data: DataRightsRequestCreate, actor: User = Depends(require_role(UserRole.patient)),
    db: Session = Depends(get_db),
):
    from uuid import uuid4
    from app.services.care_service import audit_event
    row = DataRightsRequest(
        request_id=str(uuid4()), user_id=actor.user_id,
        request_type=data.request_type, details=data.details, status="pending",
    )
    db.add(row)
    audit_event(db, actor.user_id, f"data_rights.{data.request_type}_requested", "data_rights_request", row.request_id)
    db.commit(); db.refresh(row)
    return {"request_id": row.request_id, "request_type": row.request_type, "status": row.status, "created_at": row.created_at}


@router.get("/today", response_model=PatientTodayResponse)
def today(
    day: date = Query(default_factory=lambda: datetime.now(timezone.utc).date()),
    actor: User = Depends(require_role(UserRole.patient)), db: Session = Depends(get_db),
):
    profile = current_profile(db, actor)
    return profile if isinstance(profile, JSONResponse) else patient_today(db, profile, day)


@router.post("/adherence", response_model=AdherenceDetail, status_code=status.HTTP_201_CREATED)
def adherence(
    data: AdherenceCreate,
    idempotency_key: str | None = Header(default=None, alias="Idempotency-Key", max_length=128),
    actor: User = Depends(require_role(UserRole.patient)), db: Session = Depends(get_db),
):
    profile = current_profile(db, actor)
    if isinstance(profile, JSONResponse):
        return profile
    try:
        return record_adherence(db, profile, data, idempotency_key)
    except LookupError:
        return error("PLAN_ITEM_NOT_FOUND", "This exercise is not part of your assigned plan.", 404)
    except ValueError as exc:
        if str(exc) == "ANALYSIS_EXERCISE_MISMATCH":
            return error("ANALYSIS_EXERCISE_MISMATCH", "The saved analysis belongs to a different exercise.", 422)
        if str(exc) == "CLINICAL_REVIEW_PENDING":
            return error(
                "CLINICAL_REVIEW_PENDING",
                "This response is awaiting therapist review and cannot be replaced yet.",
                409,
            )
        return error("ANALYSIS_SESSION_ACCESS_DENIED", "The saved analysis is not available to this patient.", 403)


@router.get("/appointments", response_model=list[AppointmentSummary])
def appointments(actor: User = Depends(require_role(UserRole.patient)), db: Session = Depends(get_db)):
    profile = current_profile(db, actor)
    if isinstance(profile, JSONResponse):
        return profile
    rows = db.scalars(select(Appointment).where(
        Appointment.patient_id == profile.patient_id,
    ).order_by(Appointment.starts_at.desc()).limit(100)).all()
    return [appointment_summary(row) for row in rows]


@router.get("/appointments/{appointment_id}/session-notes", response_model=list[ClinicalNoteDetail])
def visit_notes(appointment_id: str, actor: User = Depends(require_role(UserRole.patient)), db: Session = Depends(get_db)):
    profile = current_profile(db, actor)
    if isinstance(profile, JSONResponse):
        return profile
    appointment = db.scalar(select(Appointment).where(Appointment.appointment_id == appointment_id, Appointment.patient_id == profile.patient_id))
    if appointment is None:
        return error("APPOINTMENT_NOT_FOUND", "Appointment was not found.", 404)
    return appointment_notes(db, appointment_id, shared_only=True)


@router.get("/reports")
def reports(actor: User = Depends(require_role(UserRole.patient)), db: Session = Depends(get_db)):
    profile = current_profile(db, actor)
    if isinstance(profile, JSONResponse):
        return profile
    rows = db.scalars(select(ProgressReport).where(
        ProgressReport.patient_id == profile.patient_id,
        ProgressReport.shared_with_patient.is_(True),
    ).order_by(ProgressReport.created_at.desc())).all()
    return [{
        "progress_report_id": row.progress_report_id,
        "period_start": row.period_start, "period_end": row.period_end,
        "created_at": row.created_at,
        "download_url": build_artifact_url(
            f"/api/v1/artifacts/reports/{row.artifact_id}", row.artifact_id,
            "report", exercise_id="progress",
        ),
    } for row in rows]


@router.get("/notifications", response_model=list[NotificationSummary])
def notifications(
    unread_only: bool = False, actor: User = Depends(require_role(UserRole.patient)),
    db: Session = Depends(get_db),
):
    statement = select(Notification).where(Notification.user_id == actor.user_id)
    if unread_only:
        statement = statement.where(Notification.read_at.is_(None))
    rows = db.scalars(statement.order_by(Notification.created_at.desc()).limit(100)).all()
    return [notification_summary(row) for row in rows]


@router.post("/notifications/{notification_id}/read", response_model=NotificationSummary)
def read_notification(
    notification_id: str, actor: User = Depends(require_role(UserRole.patient)),
    db: Session = Depends(get_db),
):
    row = db.scalar(select(Notification).where(
        Notification.notification_id == notification_id, Notification.user_id == actor.user_id,
    ))
    if row is None:
        return error("NOTIFICATION_NOT_FOUND", "Notification was not found.", 404)
    row.read_at = datetime.now(timezone.utc)
    db.commit(); db.refresh(row)
    return notification_summary(row)
