"""Local development session-history API."""

from fastapi import APIRouter, Depends, Query, status
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from app.db.crud import delete_session, get_session, list_sessions, to_detail, to_summary
from app.db.database import get_db
from app.schemas.analysis_schema import ErrorResponse
from app.schemas.session_schema import SessionDeleteResponse, SessionDetail, SessionListResponse
from app.api.dependencies.auth import get_current_user
from app.db.models import User


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
    owner = None if current_user.role in {"admin", "therapist"} else current_user.user_id
    rows, total = list_sessions(db, exercise_id, status_filter, limit, offset, owner)
    return SessionListResponse(items=[to_summary(row) for row in rows], total=total, limit=limit, offset=offset)


@router.get("/{session_id}", response_model=SessionDetail)
def session_detail(session_id: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    row = get_session(db, session_id)
    if row is None or (current_user.role not in {"admin", "therapist"} and row.owner_user_id != current_user.user_id):
        return not_found()
    return to_detail(row)


@router.delete("/{session_id}", response_model=SessionDeleteResponse)
def remove_session(session_id: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    row = get_session(db, session_id)
    if row is None or (current_user.role not in {"admin", "therapist"} and row.owner_user_id != current_user.user_id):
        return not_found()
    delete_session(db, session_id)
    return SessionDeleteResponse(session_id=session_id)
