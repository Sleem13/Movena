"""Read authorized appointment notes; routers must check object access first."""
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.db.models import ClinicalSessionNote, User
from app.schemas.care_schema import ClinicalNoteDetail


def appointment_notes(db: Session, appointment_id: str, *, shared_only: bool):
    query = select(ClinicalSessionNote, User.full_name, User.username).outerjoin(
        User, User.user_id == ClinicalSessionNote.therapist_user_id,
    ).where(ClinicalSessionNote.appointment_id == appointment_id)
    if shared_only:
        query = query.where(ClinicalSessionNote.patient_visible.is_(True))
    rows = db.execute(query.order_by(ClinicalSessionNote.created_at.desc(), ClinicalSessionNote.note_id.desc())).all()
    return [ClinicalNoteDetail.model_validate(note).model_copy(update={'author_name': full_name or username})
            for note, full_name, username in rows]
