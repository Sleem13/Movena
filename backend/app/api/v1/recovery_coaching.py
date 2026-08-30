"""Protected Recovery & Lifestyle Coaching API."""

from fastapi import APIRouter, Depends, Query, status
from fastapi.responses import JSONResponse
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.dependencies.auth import require_patient_or_therapist
from app.api.error_responses import api_error_response
from app.db.database import get_db
from app.db.models import (
    RecoveryCoachingActionPlan, RecoveryCoachingCheckIn, RecoveryCoachingGoal, User,
)
from app.schemas.recovery_coaching_schema import (
    CoachingActionPlanCreate, CoachingActionPlanUpdate, CoachingCheckInCreate,
    CoachingFollowUpAcknowledge, CoachingGoalCreate, CoachingGoalUpdate,
    CoachingReminderPreferenceUpdate,
)
from app.services.care_service import audit_event
from app.services.recovery_coaching_service import (
    COACHING_TEMPLATES, acknowledge_follow_up, action_plan_payload,
    create_action_plan, create_goal, dashboard, goal_payload, record_check_in,
    resolve_coaching_patient, update_reminder_preference,
)

router = APIRouter(
    prefix="/api/v1/recovery-coaching", tags=["recovery-coaching"],
    dependencies=[Depends(require_patient_or_therapist)],
)


def error(code: str, message: str, status_code: int) -> JSONResponse:
    return api_error_response(code, message, status_code)


def patient_or_error(db: Session, actor: User, patient_id: str | None):
    try:
        return resolve_coaching_patient(db, actor, patient_id)
    except LookupError as exc:
        code = str(exc)
        return error(code, "A valid patient profile is required." if code == "PATIENT_PROFILE_REQUIRED" else "Patient was not found.", 409 if code == "PATIENT_PROFILE_REQUIRED" else 404)
    except PermissionError:
        return error("PATIENT_ACCESS_DENIED", "This patient is not available to your account.", 403)
    except ValueError:
        return error("PATIENT_ID_REQUIRED", "Select a patient before opening coaching records.", 422)


@router.get("/dashboard")
def coaching_dashboard(
    patient_id: str | None = Query(default=None),
    actor: User = Depends(require_patient_or_therapist), db: Session = Depends(get_db),
):
    patient = patient_or_error(db, actor, patient_id)
    return patient if isinstance(patient, JSONResponse) else dashboard(db, patient)


@router.get("/templates")
def coaching_templates(actor: User = Depends(require_patient_or_therapist)):
    return {
        "templates": COACHING_TEMPLATES,
        "clinical_review_required": True,
        "scope": "Behavior goals only; templates do not prescribe exercise dosage or treatment.",
        "can_apply_template": actor.role != "patient",
    }


@router.post("/goals", status_code=status.HTTP_201_CREATED)
def add_goal(
    data: CoachingGoalCreate, patient_id: str | None = Query(default=None),
    actor: User = Depends(require_patient_or_therapist), db: Session = Depends(get_db),
):
    patient = patient_or_error(db, actor, patient_id)
    return patient if isinstance(patient, JSONResponse) else create_goal(db, actor, patient, data)


@router.patch("/goals/{goal_id}")
def update_goal(
    goal_id: str, data: CoachingGoalUpdate, patient_id: str | None = Query(default=None),
    actor: User = Depends(require_patient_or_therapist), db: Session = Depends(get_db),
):
    patient = patient_or_error(db, actor, patient_id)
    if isinstance(patient, JSONResponse): return patient
    row = db.scalar(select(RecoveryCoachingGoal).where(
        RecoveryCoachingGoal.goal_id == goal_id, RecoveryCoachingGoal.patient_id == patient.patient_id,
    ))
    if row is None: return error("GOAL_NOT_FOUND", "Coaching goal was not found.", 404)
    row.progress_percent = data.progress_percent; row.status = data.status
    audit_event(db, actor.user_id, "recovery_coaching.goal_updated", "recovery_coaching_goal", goal_id, data.model_dump())
    db.commit(); db.refresh(row)
    return goal_payload(row)


@router.post("/check-ins")
def add_check_in(
    data: CoachingCheckInCreate, patient_id: str | None = Query(default=None),
    actor: User = Depends(require_patient_or_therapist), db: Session = Depends(get_db),
):
    patient = patient_or_error(db, actor, patient_id)
    return patient if isinstance(patient, JSONResponse) else record_check_in(db, actor, patient, data)


@router.post("/check-ins/{check_in_id}/acknowledge")
def acknowledge_check_in(
    check_in_id: str, data: CoachingFollowUpAcknowledge,
    patient_id: str | None = Query(default=None),
    actor: User = Depends(require_patient_or_therapist), db: Session = Depends(get_db),
):
    patient = patient_or_error(db, actor, patient_id)
    if isinstance(patient, JSONResponse): return patient
    row = db.scalar(select(RecoveryCoachingCheckIn).where(
        RecoveryCoachingCheckIn.check_in_id == check_in_id,
        RecoveryCoachingCheckIn.patient_id == patient.patient_id,
    ))
    if row is None: return error("CHECK_IN_NOT_FOUND", "Coaching check-in was not found.", 404)
    try:
        return acknowledge_follow_up(db, actor, patient, row, data)
    except PermissionError:
        return error("CLINICIAN_REVIEW_REQUIRED", "A clinical user must acknowledge follow-up.", 403)
    except ValueError as exc:
        messages = {
            "FOLLOW_UP_NOT_REQUIRED": "This check-in does not require clinical follow-up.",
            "FOLLOW_UP_ALREADY_ACKNOWLEDGED": "This follow-up was already acknowledged.",
            "URGENT_DISPOSITION_REQUIRED": "Urgent concerns require a contacted, scheduled, or escalated disposition.",
        }
        return error(str(exc), messages.get(str(exc), "Follow-up could not be acknowledged."), 409)


@router.put("/reminder-preference")
def save_reminder_preference(
    data: CoachingReminderPreferenceUpdate,
    patient_id: str | None = Query(default=None),
    actor: User = Depends(require_patient_or_therapist), db: Session = Depends(get_db),
):
    patient = patient_or_error(db, actor, patient_id)
    return patient if isinstance(patient, JSONResponse) else update_reminder_preference(db, actor, patient, data)


@router.post("/action-plans", status_code=status.HTTP_201_CREATED)
def add_action_plan(
    data: CoachingActionPlanCreate, patient_id: str | None = Query(default=None),
    actor: User = Depends(require_patient_or_therapist), db: Session = Depends(get_db),
):
    patient = patient_or_error(db, actor, patient_id)
    if isinstance(patient, JSONResponse): return patient
    try:
        return create_action_plan(db, actor, patient, data)
    except PermissionError:
        return error("THERAPIST_ACTION_REQUIRED", "A therapist must create and review action plans.", 403)
    except LookupError:
        return error("GOAL_NOT_FOUND", "Coaching goal was not found.", 404)


@router.patch("/action-plans/{action_plan_id}")
def update_action_plan(
    action_plan_id: str, data: CoachingActionPlanUpdate,
    patient_id: str | None = Query(default=None),
    actor: User = Depends(require_patient_or_therapist), db: Session = Depends(get_db),
):
    patient = patient_or_error(db, actor, patient_id)
    if isinstance(patient, JSONResponse): return patient
    row = db.scalar(select(RecoveryCoachingActionPlan).where(
        RecoveryCoachingActionPlan.action_plan_id == action_plan_id,
        RecoveryCoachingActionPlan.patient_id == patient.patient_id,
    ))
    if row is None: return error("ACTION_PLAN_NOT_FOUND", "Action plan was not found.", 404)
    row.status = data.status
    audit_event(db, actor.user_id, "recovery_coaching.action_plan_updated", "recovery_coaching_action_plan", action_plan_id, data.model_dump())
    db.commit(); db.refresh(row)
    return action_plan_payload(row)
