"""Protected session-history API."""

from fastapi import APIRouter, Depends, Query, status
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from app.db.crud import delete_session, get_session, list_sessions, to_detail, to_summary
from app.db.database import get_db
from app.schemas.analysis_schema import ErrorResponse
from app.schemas.session_schema import SessionDeleteResponse, SessionDetail, SessionListResponse
from app.api.dependencies.auth import get_current_user
from app.db.models import User
from app.db.models import AnalysisSession
from sqlalchemy import select, func
from app.services.care_service import accessible_session_filter, user_can_access_session


router = APIRouter(prefix="/api/v1/sessions", tags=["sessions"])


def not_found() -> JSONResponse:
    payload = ErrorResponse(error_code="SESSION_NOT_FOUND", message="Saved session was not found.")
    return JSONResponse(status_code=status.HTTP_404_NOT_FOUND, content=payload.model_dump())


@router.get("", response_model=SessionListResponse)
def recent_sessions(
    exercise_id: str | None = None,
    status_filter: str | None = Query(None, alias="status"),
    limit: int = Query(50, ge=1, le=200), offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    filters = [accessible_session_filter(current_user)]
    if exercise_id:
        filters.append(AnalysisSession.exercise_id == exercise_id)
    if status_filter:
        filters.append(AnalysisSession.status == status_filter)
    total = db.scalar(select(func.count()).select_from(AnalysisSession).where(*filters)) or 0
    rows = db.scalars(select(AnalysisSession).where(*filters).order_by(AnalysisSession.created_at.desc()).limit(limit).offset(offset)).all()
    return SessionListResponse(items=[to_summary(row) for row in rows], total=total, limit=limit, offset=offset)


@router.get("/{session_id}", response_model=SessionDetail)
def session_detail(session_id: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    row = get_session(db, session_id)
    if row is None or not user_can_access_session(db, current_user, row):
        return not_found()
    return to_detail(row)


@router.delete("/{session_id}", response_model=SessionDeleteResponse)
def remove_session(session_id: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    row = get_session(db, session_id)
    if row is None or not user_can_access_session(db, current_user, row):
        return not_found()
    if row.patient_id and current_user.role == "therapist":
        return JSONResponse(status_code=403, content={"error_code": "CLINICAL_RECORD_PRESERVED", "message": "Patient records cannot be deleted from a therapist workspace."})
    delete_session(db, session_id)
    return SessionDeleteResponse(session_id=session_id)
