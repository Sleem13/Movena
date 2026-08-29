"""Role-protected therapist dashboard API."""

from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from app.db.crud import (
    assign_session_to_patient, create_exercise_plan, create_patient_profile, delete_patient_profile,
    get_patient_profile, get_patient_progress_summary, get_therapist_dashboard_summary,
    list_exercise_plans, list_patient_sessions, to_exercise_plan_detail,
    to_summary, update_exercise_plan_status, update_patient_profile,
)
from app.db.models import User
from app.db.database import get_db
from app.schemas.analysis_schema import ErrorResponse
from app.schemas.patient_schema import (
    ExercisePlanCreate, ExercisePlanDetail, ExercisePlanStatusUpdate,
    PatientCreate, PatientDetail, PatientSummary, PatientUpdate,
)
from app.schemas.session_schema import SessionDeleteResponse, SessionSummary
from app.schemas.therapist_schema import PROTOTYPE_WARNING, TherapistDashboardSummary
from app.api.dependencies.auth import require_therapist
from app.services.care_service import audit_event, ensure_assignment, list_patients_for_therapist, user_can_access_patient


router = APIRouter(prefix="/api/v1/therapist", tags=["therapist"], dependencies=[Depends(require_therapist)])


def error(code: str, message: str, status_code: int = status.HTTP_404_NOT_FOUND) -> JSONResponse:
    return JSONResponse(status_code=status_code, content=ErrorResponse(error_code=code, message=message).model_dump())


def patient_summary(db: Session, row) -> PatientSummary:
    progress = get_patient_progress_summary(db, row.patient_id)
    return PatientSummary(
        patient_id=row.patient_id, display_name=row.display_name, age_group=row.age_group,
        sex=row.sex, clinical_group=row.clinical_group, created_at=row.created_at,
        updated_at=row.updated_at, session_count=progress.total_sessions,
        latest_session_date=progress.latest_session_date,
    )


@router.get("/dashboard", response_model=TherapistDashboardSummary)
def dashboard(actor: User = Depends(require_therapist), db: Session = Depends(get_db)):
    return get_therapist_dashboard_summary(
        db, therapist_user_id=actor.user_id if actor.role == "therapist" else None
    )


@router.get("/patients", response_model=list[PatientSummary])
def patients(actor: User = Depends(require_therapist), db: Session = Depends(get_db)):
    return [patient_summary(db, row) for row in list_patients_for_therapist(db, actor)]


@router.post("/patients", response_model=PatientDetail, status_code=status.HTTP_201_CREATED)
def create_patient(
    data: PatientCreate, actor: User = Depends(require_therapist), db: Session = Depends(get_db)
):
    row = create_patient_profile(db, data)
    if actor.role == "therapist":
        ensure_assignment(db, actor.user_id, row.patient_id, actor.user_id)
        db.commit()
    summary = patient_summary(db, row)
    return PatientDetail(**summary.model_dump(), notes=row.notes,
                         progress=get_patient_progress_summary(db, row.patient_id),
                         prototype_warning=PROTOTYPE_WARNING)


@router.get("/patients/{patient_id}", response_model=PatientDetail)
def patient_detail(
    patient_id: str, actor: User = Depends(require_therapist), db: Session = Depends(get_db)
):
    row = get_patient_profile(db, patient_id)
    if row is None:
        return error("PATIENT_NOT_FOUND", "Patient profile was not found.")
    if not user_can_access_patient(db, actor, patient_id):
        return error("PATIENT_ACCESS_DENIED", "This patient is not assigned to you.", 403)
    summary = patient_summary(db, row)
    return PatientDetail(**summary.model_dump(), notes=row.notes,
                         progress=get_patient_progress_summary(db, patient_id),
                         prototype_warning=PROTOTYPE_WARNING)


@router.patch("/patients/{patient_id}", response_model=PatientDetail)
def patch_patient(
    patient_id: str, data: PatientUpdate, actor: User = Depends(require_therapist),
    db: Session = Depends(get_db),
):
    if not user_can_access_patient(db, actor, patient_id):
        return error("PATIENT_ACCESS_DENIED", "This patient is not assigned to you.", 403)
    row = update_patient_profile(db, patient_id, data)
    if row is None:
        return error("PATIENT_NOT_FOUND", "Patient profile was not found.")
    summary = patient_summary(db, row)
    return PatientDetail(**summary.model_dump(), notes=row.notes,
                         progress=get_patient_progress_summary(db, patient_id),
                         prototype_warning=PROTOTYPE_WARNING)


@router.delete("/patients/{patient_id}", response_model=SessionDeleteResponse)
def remove_patient(
    patient_id: str, actor: User = Depends(require_therapist), db: Session = Depends(get_db)
):
    if not user_can_access_patient(db, actor, patient_id):
        return error("PATIENT_ACCESS_DENIED", "This patient is not assigned to you.", 403)
    if not delete_patient_profile(db, patient_id):
        return error("PATIENT_NOT_FOUND", "Patient profile was not found.")
    return SessionDeleteResponse(session_id=patient_id)


@router.get("/patients/{patient_id}/sessions", response_model=list[SessionSummary])
def patient_sessions(
    patient_id: str, actor: User = Depends(require_therapist), db: Session = Depends(get_db)
):
    if get_patient_profile(db, patient_id) is None:
        return error("PATIENT_NOT_FOUND", "Patient profile was not found.")
    if not user_can_access_patient(db, actor, patient_id):
        return error("PATIENT_ACCESS_DENIED", "This patient is not assigned to you.", 403)
    return [to_summary(row) for row in list_patient_sessions(db, patient_id)]


@router.post("/patients/{patient_id}/sessions/{session_id}", response_model=SessionSummary)
def assign_session(
    patient_id: str, session_id: str, actor: User = Depends(require_therapist),
    db: Session = Depends(get_db),
):
    if not user_can_access_patient(db, actor, patient_id):
        return error("PATIENT_ACCESS_DENIED", "This patient is not assigned to you.", 403)
    if get_patient_profile(db, patient_id) is None:
        return error("PATIENT_NOT_FOUND", "Patient profile was not found.")
    from app.db.crud import get_session
    if get_session(db, session_id) is None:
        return error("SESSION_NOT_FOUND", "Saved session was not found.")
    return to_summary(assign_session_to_patient(db, patient_id, session_id))


@router.get("/patients/{patient_id}/progress")
def patient_progress(
    patient_id: str, actor: User = Depends(require_therapist), db: Session = Depends(get_db)
):
    if not user_can_access_patient(db, actor, patient_id):
        return error("PATIENT_ACCESS_DENIED", "This patient is not assigned to you.", 403)
    if get_patient_profile(db, patient_id) is None:
        return error("PATIENT_NOT_FOUND", "Patient profile was not found.")
    return get_patient_progress_summary(db, patient_id)


@router.get("/patients/{patient_id}/exercise-plans", response_model=list[ExercisePlanDetail])
def patient_exercise_plans(
    patient_id: str, actor: User = Depends(require_therapist), db: Session = Depends(get_db)
):
    if not user_can_access_patient(db, actor, patient_id):
        return error("PATIENT_ACCESS_DENIED", "This patient is not assigned to you.", 403)
    if get_patient_profile(db, patient_id) is None:
        return error("PATIENT_NOT_FOUND", "Patient profile was not found.")
    return [to_exercise_plan_detail(row) for row in list_exercise_plans(db, patient_id)]


@router.post(
    "/patients/{patient_id}/exercise-plans",
    response_model=ExercisePlanDetail,
    status_code=status.HTTP_201_CREATED,
)
def add_patient_exercise_plan(
    patient_id: str,
    data: ExercisePlanCreate,
    db: Session = Depends(get_db),
    actor: User = Depends(require_therapist),
):
    if not user_can_access_patient(db, actor, patient_id):
        return error("PATIENT_ACCESS_DENIED", "This patient is not assigned to you.", 403)
    if get_patient_profile(db, patient_id) is None:
        return error("PATIENT_NOT_FOUND", "Patient profile was not found.")
    row = create_exercise_plan(db, patient_id, data, actor.user_id)
    audit_event(db, actor.user_id, "exercise_plan.created", "exercise_plan", row.plan_id, {
        "patient_id": patient_id, "item_count": len(row.items), "history_preserved": True,
    })
    db.commit()
    return to_exercise_plan_detail(row)


@router.patch(
    "/patients/{patient_id}/exercise-plans/{plan_id}", response_model=ExercisePlanDetail
)
def patch_patient_exercise_plan(
    patient_id: str,
    plan_id: str,
    data: ExercisePlanStatusUpdate,
    actor: User = Depends(require_therapist),
    db: Session = Depends(get_db),
):
    if not user_can_access_patient(db, actor, patient_id):
        return error("PATIENT_ACCESS_DENIED", "This patient is not assigned to you.", 403)
    if get_patient_profile(db, patient_id) is None:
        return error("PATIENT_NOT_FOUND", "Patient profile was not found.")
    row = update_exercise_plan_status(db, patient_id, plan_id, data.status)
    if row is None:
        return error("EXERCISE_PLAN_NOT_FOUND", "Exercise plan was not found.")
    audit_event(db, actor.user_id, "exercise_plan.status_changed", "exercise_plan", row.plan_id, {
        "patient_id": patient_id, "status": data.status,
    })
    db.commit()
    return to_exercise_plan_detail(row)
