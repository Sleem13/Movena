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
    RecoveryCoachingGoal, RecoveryCoachingReminderPreference,
    TherapistPatientAssignment, User, utc_now,
)
from app.schemas.recovery_coaching_schema import (
    CoachingActionPlanCreate, CoachingCheckInCreate, CoachingFollowUpAcknowledge,
    CoachingGoalCreate, CoachingReminderPreferenceUpdate,
)
from app.services.care_service import audit_event, create_notification, patient_for_user, user_can_access_patient


COACHING_DISCLAIMER = (
    "Recovery coaching supports self-directed habits and accountability. It does not provide diagnosis, "
    "psychotherapy, nutrition or medication advice, emergency counseling, or autonomous exercise prescription."
)

COACHING_TEMPLATES = (
    {
        "template_id": "general-routine-consistency",
        "pathway": "General rehabilitation",
        "domain": "adherence",
        "title": "Build a consistent rehabilitation routine",
        "specific_action": "Complete the clinician-approved rehabilitation routine at the agreed time on planned days.",
        "measurement": "Record whether the agreed routine was completed on each planned day.",
        "why_important": "Make the rehabilitation plan easier to follow consistently.",
    },
    {
        "template_id": "orthopedic-participation",
        "pathway": "Orthopedic recovery",
        "domain": "participation",
        "title": "Return to one meaningful daily activity",
        "specific_action": "Practice one patient-selected daily activity within the clinician-agreed precautions and limits.",
        "measurement": "Record completion and confidence without changing the prescribed dosage.",
        "why_important": "Reconnect rehabilitation progress with a meaningful life role.",
    },
    {
        "template_id": "neurologic-support-routine",
        "pathway": "Neurologic rehabilitation",
        "domain": "social_support",
        "title": "Use agreed support for home practice",
        "specific_action": "Arrange the agreed support person or accessibility setup before clinician-approved home practice.",
        "measurement": "Record whether the support setup was available on planned practice days.",
        "why_important": "Reduce access barriers while preserving safety and independence.",
    },
    {
        "template_id": "persistent-symptom-pacing",
        "pathway": "Persistent symptom management",
        "domain": "activity",
        "title": "Use a consistent activity window",
        "specific_action": "Use the clinician-agreed activity window and pause for clinical review if symptoms change or worsen.",
        "measurement": "Record completion and the main barrier; do not self-progress treatment dosage.",
        "why_important": "Support a predictable routine without using coaching to modify treatment.",
    },
    {
        "template_id": "sleep-routine",
        "pathway": "Recovery routine",
        "domain": "sleep_routine",
        "title": "Create a consistent wind-down routine",
        "specific_action": "Begin the patient-selected non-clinical wind-down routine at a consistent time.",
        "measurement": "Record routine completion and perceived sleep quality at the next check-in.",
        "why_important": "Support recovery habits without treating or diagnosing a sleep disorder.",
    },
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
        "reviewed_at": row.reviewed_at, "reviewed_by_user_id": row.reviewed_by_user_id,
        "review_disposition": row.review_disposition, "review_note": row.review_note,
    }


def action_plan_payload(row: RecoveryCoachingActionPlan) -> dict:
    return {
        "action_plan_id": row.action_plan_id, "goal_id": row.goal_id,
        "patient_id": row.patient_id, "action_step": row.action_step,
        "frequency": row.frequency, "support_needed": row.support_needed,
        "review_date": row.review_date, "patient_agreed": row.patient_agreed,
        "status": row.status, "created_at": row.created_at, "updated_at": row.updated_at,
    }


def reminder_preference_payload(row: RecoveryCoachingReminderPreference | None) -> dict:
    if row is None:
        return {
            "preference_id": None, "enabled": False, "local_time": "19:00",
            "cadence": "daily", "missed_follow_up_days": 3, "patient_agreed": False,
        }
    return {
        "preference_id": row.preference_id, "enabled": row.enabled,
        "local_time": row.local_time, "cadence": row.cadence,
        "missed_follow_up_days": row.missed_follow_up_days,
        "patient_agreed": row.patient_agreed, "updated_at": row.updated_at,
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
    reminder_preference = db.scalar(select(RecoveryCoachingReminderPreference).where(
        RecoveryCoachingReminderPreference.patient_id == patient.patient_id,
    ))
    settings = get_settings()
    return {
        "patient": {"patient_id": patient.patient_id, "display_name": patient.display_name},
        "goals": [goal_payload(row) for row in goals],
        "check_ins": [check_in_payload(row) for row in check_ins],
        "action_plans": [action_plan_payload(row) for row in plans],
        "reminder_preference": reminder_preference_payload(reminder_preference),
        "trends": [check_in_payload(row) for row in reversed(check_ins)],
        "summary": {
            "active_goals": sum(row.status == "active" for row in goals),
            "completed_goals": sum(row.status == "completed" for row in goals),
            "check_ins_30d": len(check_ins),
            "average_confidence": round(mean(row.recovery_confidence for row in check_ins), 1) if check_ins else None,
            "follow_up_needed": sum(row.coaching_state != "ready" for row in check_ins),
            "unacknowledged_follow_up": sum(
                row.coaching_state != "ready" and row.reviewed_at is None for row in check_ins
            ),
        },
        "scope": {
            "disclaimer": COACHING_DISCLAIMER,
            "domains": ["mobility_routine", "sleep_routine", "activity", "stress_management", "participation", "adherence", "social_support"],
            "urgent_instruction": settings.clinical_escalation_instruction,
            "urgent_contact": settings.clinical_escalation_contact,
            "organization": settings.clinical_organization_name,
            "escalation_configured": bool(settings.clinical_escalation_contact.strip()),
            "monitoring_statement": "Check-ins are not monitored in real time and do not guarantee a response within a specific period.",
            "review_expectation": "Clinical teams must follow their organization-defined review and escalation policy.",
            "informal_ratings_separate_from_proms": True,
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


def acknowledge_follow_up(
    db: Session, actor: User, patient: PatientProfile,
    row: RecoveryCoachingCheckIn, data: CoachingFollowUpAcknowledge,
) -> dict:
    if actor.role == "patient":
        raise PermissionError("CLINICIAN_REVIEW_REQUIRED")
    if row.coaching_state == "ready":
        raise ValueError("FOLLOW_UP_NOT_REQUIRED")
    if row.reviewed_at is not None:
        raise ValueError("FOLLOW_UP_ALREADY_ACKNOWLEDGED")
    if row.coaching_state == "urgent_escalation" and data.disposition == "reviewed_no_additional_action":
        raise ValueError("URGENT_DISPOSITION_REQUIRED")
    row.reviewed_at = utc_now()
    row.reviewed_by_user_id = actor.user_id
    row.review_disposition = data.disposition
    row.review_note = data.note
    audit_event(
        db, actor.user_id, "recovery_coaching.follow_up_acknowledged",
        "recovery_coaching_check_in", row.check_in_id,
        {
            "patient_id": patient.patient_id,
            "coaching_state": row.coaching_state,
            "disposition": data.disposition,
            "clinician_attestation": True,
        },
    )
    if patient.user_id:
        create_notification(
            db, patient.user_id, "recovery_coaching_reviewed",
            "Recovery check-in reviewed",
            "Your care team reviewed the recovery check-in that required follow-up.",
            action_url="/recovery-coaching",
            dedup_key=f"recovery-checkin-reviewed:{row.check_in_id}",
        )
    db.commit(); db.refresh(row)
    return check_in_payload(row)


def update_reminder_preference(
    db: Session, actor: User, patient: PatientProfile,
    data: CoachingReminderPreferenceUpdate,
) -> dict:
    row = db.scalar(select(RecoveryCoachingReminderPreference).where(
        RecoveryCoachingReminderPreference.patient_id == patient.patient_id,
    ))
    created = row is None
    if row is None:
        row = RecoveryCoachingReminderPreference(
            preference_id=str(uuid4()), patient_id=patient.patient_id,
            created_by_user_id=actor.user_id,
        )
        db.add(row)
    for key, value in data.model_dump().items():
        setattr(row, key, value)
    audit_event(
        db, actor.user_id,
        f"recovery_coaching.reminder_preference_{'created' if created else 'updated'}",
        "recovery_coaching_reminder_preference", row.preference_id,
        {
            "patient_id": patient.patient_id, "enabled": row.enabled,
            "cadence": row.cadence, "missed_follow_up_days": row.missed_follow_up_days,
            "patient_agreed": True,
        },
    )
    db.commit(); db.refresh(row)
    return reminder_preference_payload(row)
