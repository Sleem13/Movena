"""Role-scoped care team and invitation management."""
import hashlib
from typing import Literal

from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel, Field, field_validator
from app.schemas.auth_schema import UserRegisterRequest
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.api.dependencies.auth import get_current_user, require_admin, require_role
from app.db.database import get_db
from app.db.models import CareInvitation, PatientProfile, TherapistPatientAssignment, User
from app.services import connection_service as service

router = APIRouter(prefix="/api/v1", tags=["care-connections"])


class InvitationCreate(BaseModel):
    email: str = Field(max_length=320)
    patient_id: str | None = None

    @field_validator("email")
    @classmethod
    def normalize_email(cls, value):
        if any(char.isspace() for char in value.strip()) or value.count("@") != 1:
            raise ValueError("A valid email address is required.")
        return UserRegisterRequest.valid_email(value)


class InvitationResponse(BaseModel):
    action: Literal["accept", "decline"]
    token: str | None = Field(None, max_length=200)


class EndConnection(BaseModel):
    reason: str | None = Field(None, max_length=1000)


class InvitationLookup(BaseModel):
    token: str = Field(min_length=20, max_length=200)


@router.get("/connections")
def connections(actor: User = Depends(get_current_user), db: Session = Depends(get_db)):
    statement = select(TherapistPatientAssignment)
    if actor.role == "patient":
        statement = statement.join(PatientProfile, PatientProfile.patient_id == TherapistPatientAssignment.patient_id).where(PatientProfile.user_id == actor.user_id)
    elif actor.role == "therapist":
        statement = statement.where(TherapistPatientAssignment.therapist_user_id == actor.user_id)
    elif actor.role not in {"admin", "super_admin"}:
        service.fail("This workspace requires a care role.", status=403)
    return [service.summary(db, row) for row in db.scalars(statement.order_by(TherapistPatientAssignment.assigned_at.desc()))]


@router.post("/connections/{assignment_id}/end")
def end(assignment_id: str, data: EndConnection, actor: User = Depends(get_current_user), db: Session = Depends(get_db)):
    row = service.end_connection(db, actor, assignment_id, (data.reason or "").strip() or None)
    db.commit()
    return service.summary(db, row)


@router.get("/care-invitations")
def invitations(actor: User = Depends(get_current_user), db: Session = Depends(get_db)):
    statement = select(CareInvitation)
    if actor.role == "therapist":
        statement = statement.where(CareInvitation.therapist_user_id == actor.user_id)
    elif actor.role == "patient":
        if not actor.is_verified:
            service.fail("Verify your email to view invitations.", "EMAIL_NOT_VERIFIED", 403)
        statement = statement.where(CareInvitation.email == actor.email.strip().lower())
    else:
        service.fail("Invitations are available to patients and therapists.", status=403)
    return [service.invitation_summary(db, row) for row in db.scalars(statement.order_by(CareInvitation.updated_at.desc()))]


@router.post("/care-invitations")
def create(data: InvitationCreate, actor: User = Depends(require_role("therapist")), db: Session = Depends(get_db)):
    row, token = service.invite(db, actor, str(data.email), data.patient_id)
    db.commit()
    service.deliver_invitation(db, row, token)
    return service.invitation_summary(db, row)


@router.post("/care-invitations/lookup")
def lookup(data: InvitationLookup, actor: User = Depends(require_role("patient")), db: Session = Depends(get_db)):
    row = db.scalar(select(CareInvitation).where(CareInvitation.token_hash == hashlib.sha256(data.token.encode()).hexdigest()))
    if not row or actor.role != "patient" or not actor.is_verified or row.email != actor.email.strip().lower():
        service.fail("Use the invited, verified patient account and a current invitation link.", status=403)
    return service.invitation_summary(db, row)


@router.post("/care-invitations/{invitation_id}/respond")
def respond(invitation_id: str, data: InvitationResponse, actor: User = Depends(require_role("patient")), db: Session = Depends(get_db)):
    row = service.respond(db, actor, invitation_id, data.action, data.token)
    db.commit()
    return service.invitation_summary(db, row)


@router.post("/care-invitations/{invitation_id}/{action}")
def manage(invitation_id: str, action: Literal["resend", "cancel"], actor: User = Depends(require_role("therapist")), db: Session = Depends(get_db)):
    service.lock_therapist(db, actor.user_id)
    service.active_user(db, actor.user_id, "therapist")
    row = db.scalar(select(CareInvitation).where(CareInvitation.invitation_id == invitation_id, CareInvitation.therapist_user_id == actor.user_id))
    if not row:
        service.fail("Invitation was not found.", status=404)
    if action == "resend":
        if row.status == "accepted":
            service.fail("Create a new invitation to reconnect.")
        row, token = service.invite(db, actor, row.email, resend_id=invitation_id)
        db.commit()
        service.deliver_invitation(db, row, token)
    else:
        if row.status != "pending":
            service.fail("Only pending invitations can be cancelled.")
        row.status, row.token_hash = "cancelled", None
        service.audit_event(db, actor.user_id, "connection.invitation_cancelled", "invitation", row.invitation_id)
        db.commit()
    return service.invitation_summary(db, row)


@router.get("/admin/assignment-options")
def options(q: str = Query("", max_length=120), unassigned: bool = False,
            actor: User = Depends(require_admin), db: Session = Depends(get_db)):
    patients = select(PatientProfile).where(PatientProfile.display_name.ilike(f"%{q}%"))
    if unassigned:
        patients = patients.where(~select(TherapistPatientAssignment.id).where(
            TherapistPatientAssignment.patient_id == PatientProfile.patient_id,
            TherapistPatientAssignment.status == "active").exists())
    return {
        "patients": [{"patient_id": p.patient_id, "name": p.display_name} for p in db.scalars(patients.order_by(PatientProfile.display_name).limit(100))],
        "therapists": [{"user_id": u.user_id, "name": u.full_name or u.email} for u in db.scalars(select(User).where(
            User.role == "therapist", User.is_active.is_(True), User.account_status == "active").order_by(User.full_name))],
    }
