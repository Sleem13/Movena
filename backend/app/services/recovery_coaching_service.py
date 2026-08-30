"""Role-scoped recovery coaching workflows with explicit clinical boundaries."""

from __future__ import annotations

from datetime import date, timedelta
from statistics import mean
from uuid import uuid4

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.db.models import (
    PatientProfile, RecoveryCoachingActionPlan, RecoveryCoachingCheckIn,
    RecoveryCoachingGoal, TherapistPatientAssignment, User,
)
from app.schemas.recovery_coaching_schema import (
    CoachingActionPlanCreate, CoachingCheckInCreate, CoachingGoalCreate,
)
from app.services.care_service import audit_event, create_notification, patient_for_user, user_can_access_patient


COACHING_DISCLAIMER = (
    "Recovery coaching supports self-directed habits and accountability. It does not provide diagnosis, "
    "psychotherapy, nutrition or medication advice, emergency counseling, or autonomous exercise prescription."
)


def resolve_coaching_patient(db: Session, actor: User, patient_id: str | None) -> PatientProfile:
    if actor.role == "patient":
        profile = patient_for_user(db, actor.user_id)
        if profile is None:
            raise LookupError("PATIENT_PROFILE_REQUIRED")
        if patient_id and patient_id != profile.patient_id:
            raise PermissionError("PATIENT_ACCESS_DENIED")
        return profile
    if not patient_id:
        raise ValueError("PATIENT_ID_REQUIRED")
    profile = db.scalar(select(PatientProfile).where(PatientProfile.patient_id == patient_id))
    if profile is None:
        raise LookupError("PATIENT_NOT_FOUND")
    if not user_can_access_patient(db, actor, patient_id):
        raise PermissionError("PATIENT_ACCESS_DENIED")
    return profile


def goal_payload(row: RecoveryCoachingGoal) -> dict:
    return {
        "goal_id": row.goal_id, "patient_id": row.patient_id, "domain": row.domain,
        "title": row.title, "specific_action": row.specific_action,
        "measurement": row.measurement, "why_important": row.why_important,
        "target_date": row.target_date, "confidence": row.confidence,
        "progress_percent": row.progress_percent, "status": row.status,
        "patient_agreed": row.patient_agreed, "created_at": row.created_at,
        "updated_at": row.updated_at,
    }


def check_in_payload(row: RecoveryCoachingCheckIn) -> dict:
    return {
        "check_in_id": row.check_in_id, "patient_id": row.patient_id,
        "check_in_date": row.check_in_date, "energy": row.energy,
        "sleep_quality": row.sleep_quality, "stress": row.stress,
        "recovery_confidence": row.recovery_confidence,
        "activity_minutes": row.activity_minutes, "barrier_category": row.barrier_category,
        "barrier_note": row.barrier_note, "symptoms_changed": row.symptoms_changed,
        "urgent_concern": row.urgent_concern, "coaching_state": row.coaching_state,
        "supportive_prompt": row.supportive_prompt, "created_at": row.created_at,
    }


def action_plan_payload(row: RecoveryCoachingActionPlan) -> dict:
    return {
        "action_plan_id": row.action_plan_id, "goal_id": row.goal_id,
        "patient_id": row.patient_id, "action_step": row.action_step,
        "frequency": row.frequency, "support_needed": row.support_needed,
        "review_date": row.review_date, "patient_agreed": row.patient_agreed,
        "status": row.status, "created_at": row.created_at, "updated_at": row.updated_at,
    }


def dashboard(db: Session, patient: PatientProfile) -> dict:
    goals = db.scalars(select(RecoveryCoachingGoal).where(
        RecoveryCoachingGoal.patient_id == patient.patient_id,
    ).order_by(RecoveryCoachingGoal.created_at.desc())).all()
    check_ins = db.scalars(select(RecoveryCoachingCheckIn).where(
        RecoveryCoachingCheckIn.patient_id == patient.patient_id,
        RecoveryCoachingCheckIn.check_in_date >= date.today() - timedelta(days=29),
    ).order_by(RecoveryCoachingCheckIn.check_in_date.desc())).all()
    plans = db.scalars(select(RecoveryCoachingActionPlan).where(
        RecoveryCoachingActionPlan.patient_id == patient.patient_id,
    ).order_by(RecoveryCoachingActionPlan.review_date.desc())).all()
    settings = get_settings()
    return {
        "patient": {"patient_id": patient.patient_id, "display_name": patient.display_name},
        "goals": [goal_payload(row) for row in goals],
        "check_ins": [check_in_payload(row) for row in check_ins],
        "action_plans": [action_plan_payload(row) for row in plans],
        "summary": {
            "active_goals": sum(row.status == "active" for row in goals),
            "completed_goals": sum(row.status == "completed" for row in goals),
            "check_ins_30d": len(check_ins),
            "average_confidence": round(mean(row.recovery_confidence for row in check_ins), 1) if check_ins else None,
            "follow_up_needed": sum(row.coaching_state != "ready" for row in check_ins),
        },
        "scope": {
            "disclaimer": COACHING_DISCLAIMER,
            "domains": ["mobility_routine", "sleep_routine", "activity", "stress_management", "participation", "adherence", "social_support"],
            "urgent_instruction": settings.clinical_escalation_instruction,
            "urgent_contact": settings.clinical_escalation_contact,
            "organization": settings.clinical_organization_name,
        },
    }


def create_goal(db: Session, actor: User, patient: PatientProfile, data: CoachingGoalCreate) -> dict:
    row = RecoveryCoachingGoal(
        goal_id=str(uuid4()), patient_id=patient.patient_id, created_by_user_id=actor.user_id,
        status="proposed" if actor.role == "patient" else "active",
        **data.model_dump(exclude={"scope_acknowledged"}),
    )
    db.add(row)
    audit_event(db, actor.user_id, "recovery_coaching.goal_created", "recovery_coaching_goal", row.goal_id, {
        "patient_id": patient.patient_id, "domain": row.domain, "status": row.status,
    })
    db.commit(); db.refresh(row)
    return goal_payload(row)


def _coaching_response(data: CoachingCheckInCreate) -> tuple[str, str]:
    settings = get_settings()
    if data.urgent_concern:
        contact = f" Contact {settings.clinical_organization_name} at {settings.clinical_escalation_contact}." if settings.clinical_escalation_contact else ""
        return "urgent_escalation", f"Coaching is paused. {settings.clinical_escalation_instruction}{contact}"
    if data.symptoms_changed:
        return "clinical_follow_up", "Pause progression and contact your treating clinician to review the new or worsening symptoms."
    if data.recovery_confidence <= 2:
        return "review_plan", "Choose a smaller action step you feel more confident completing and review it with your clinician."
    if data.barrier_category != "none":
        return "review_plan", "Use the barrier you identified to adjust the next action step with your clinician or coach."
    return "ready", "Continue the agreed action step and record what helped at the next check-in."


def record_check_in(db: Session, actor: User, patient: PatientProfile, data: CoachingCheckInCreate) -> dict:
    state, prompt = _coaching_response(data)
    row = db.scalar(select(RecoveryCoachingCheckIn).where(
        RecoveryCoachingCheckIn.patient_id == patient.patient_id,
        RecoveryCoachingCheckIn.check_in_date == data.check_in_date,
    ))
    created = row is None
    if row is None:
        row = RecoveryCoachingCheckIn(
            check_in_id=str(uuid4()), patient_id=patient.patient_id,
            created_by_user_id=actor.user_id, coaching_state=state,
            supportive_prompt=prompt, **data.model_dump(exclude={"scope_acknowledged"}),
        )
        db.add(row)
    else:
        for key, value in data.model_dump(exclude={"scope_acknowledged", "check_in_date"}).items():
            setattr(row, key, value)
        row.coaching_state = state; row.supportive_prompt = prompt; row.created_by_user_id = actor.user_id
    if state != "ready":
        therapist_ids = db.scalars(select(TherapistPatientAssignment.therapist_user_id).where(
            TherapistPatientAssignment.patient_id == patient.patient_id,
            TherapistPatientAssignment.status == "active",
        )).all()
        for therapist_id in therapist_ids:
            create_notification(
                db, therapist_id, "recovery_coaching_follow_up", "Recovery coaching follow-up",
                f"{patient.display_name} submitted a check-in requiring {state.replace('_', ' ')}.",
                action_url="/recovery-coaching",
                dedup_key=f"recovery-checkin:{row.check_in_id}:{therapist_id}:{state}",
            )
    audit_event(db, actor.user_id, f"recovery_coaching.check_in_{'created' if created else 'updated'}", "recovery_coaching_check_in", row.check_in_id, {
        "patient_id": patient.patient_id, "coaching_state": state,
        "symptoms_changed": data.symptoms_changed, "urgent_concern": data.urgent_concern,
    })
    db.commit(); db.refresh(row)
    return check_in_payload(row)


def create_action_plan(db: Session, actor: User, patient: PatientProfile, data: CoachingActionPlanCreate) -> dict:
    if actor.role == "patient":
        raise PermissionError("THERAPIST_ACTION_REQUIRED")
    goal = db.scalar(select(RecoveryCoachingGoal).where(
        RecoveryCoachingGoal.goal_id == data.goal_id,
        RecoveryCoachingGoal.patient_id == patient.patient_id,
    ))
    if goal is None:
        raise LookupError("GOAL_NOT_FOUND")
    row = RecoveryCoachingActionPlan(
        action_plan_id=str(uuid4()), patient_id=patient.patient_id,
        created_by_user_id=actor.user_id, **data.model_dump(),
    )
    goal.status = "active"
    db.add(row)
    audit_event(db, actor.user_id, "recovery_coaching.action_plan_created", "recovery_coaching_action_plan", row.action_plan_id, {
        "patient_id": patient.patient_id, "goal_id": goal.goal_id, "patient_agreed": True,
    })
    db.commit(); db.refresh(row)
    return action_plan_payload(row)
