"""Build the de-identified Super Admin operations workflow snapshot."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from zoneinfo import ZoneInfo

from sqlalchemy import and_, exists, func, or_, select
from sqlalchemy.orm import Session

from app.db.models import (
    Appointment,
    AuditLog,
    DataRightsRequest,
    ExercisePlan,
    Order,
    Notification,
    PatientProfile,
    Payment,
    ProgressReport,
    Refund,
    TherapistPatientAssignment,
    User,
    UserConsent,
)
from app.services.notification_service import PASSWORD_RESET_EMAIL_FAILED


CAIRO = ZoneInfo("Africa/Cairo")
PRIORITY_RANK = {"high": 0, "medium": 1, "low": 2}


def _count(db: Session, statement) -> int:
    return int(db.scalar(statement) or 0)


def _ref(kind: str, value: str | int | None) -> str:
    if value is None:
        return "System"
    text = str(value)
    return f"{kind} …{text[-8:]}"


def _age_seconds(created_at: datetime | None, now: datetime) -> int:
    if created_at is None:
        return 0
    if created_at.tzinfo is None:
        created_at = created_at.replace(tzinfo=timezone.utc)
    return max(0, int((now - created_at.astimezone(timezone.utc)).total_seconds()))


def _stage(key: str, total: int, attention_count: int) -> dict:
    return {
        "key": key,
        "total": total,
        "attention_count": attention_count,
        "status": "attention" if attention_count else "on_track",
    }


def _clinical_goal(key: str, attention_count: int) -> dict:
    return {
        "key": key,
        "attention_count": attention_count,
        "status": "attention" if attention_count else "on_track",
    }


def build_admin_workflow(
    db: Session, *, actor_user_id: str | None = None,
    now: datetime | None = None, queue_limit: int = 25,
) -> dict:
    current = (now or datetime.now(timezone.utc)).astimezone(timezone.utc)
    local_now = current.astimezone(CAIRO)
    local_start = datetime.combine(local_now.date(), datetime.min.time(), tzinfo=CAIRO)
    local_end = local_start + timedelta(days=1)
    utc_start, utc_end = local_start.astimezone(timezone.utc), local_end.astimezone(timezone.utc)

    active_assignment = exists(select(TherapistPatientAssignment.id).where(
        TherapistPatientAssignment.patient_id == PatientProfile.patient_id,
        TherapistPatientAssignment.status == "active",
    ))
    active_plan = exists(select(ExercisePlan.id).where(
        ExercisePlan.patient_id == PatientProfile.patient_id,
        ExercisePlan.status == "active",
    ))
    upcoming_appointment = exists(select(Appointment.id).where(
        Appointment.patient_id == PatientProfile.patient_id,
        Appointment.status.in_(["scheduled", "confirmed"]),
        Appointment.ends_at >= current,
    ))
    required_privacy = exists(select(UserConsent.id).where(
        UserConsent.user_id == PatientProfile.user_id,
        UserConsent.consent_type == "privacy",
        UserConsent.accepted.is_(True),
    ))
    required_care = exists(select(UserConsent.id).where(
        UserConsent.user_id == PatientProfile.user_id,
        UserConsent.consent_type == "care_data",
        UserConsent.accepted.is_(True),
    ))

    users = _count(db, select(func.count()).select_from(User))
    patients = _count(db, select(func.count()).select_from(PatientProfile))
    assignments = _count(db, select(func.count()).select_from(TherapistPatientAssignment).where(
        TherapistPatientAssignment.status == "active"
    ))
    appointments = _count(db, select(func.count()).select_from(Appointment))
    paid_orders = _count(db, select(func.count()).select_from(Order).where(Order.status == "paid"))

    missing_consent = _count(db, select(func.count()).select_from(PatientProfile).where(
        or_(~required_privacy, ~required_care)
    ))
    unassigned = _count(db, select(func.count()).select_from(PatientProfile).where(~active_assignment))
    without_plan = _count(db, select(func.count()).select_from(PatientProfile).where(
        active_assignment, ~active_plan
    ))
    without_appointment = _count(db, select(func.count()).select_from(PatientProfile).where(
        active_plan, ~upcoming_appointment
    ))
    active_plans = _count(db, select(func.count()).select_from(ExercisePlan).where(ExercisePlan.status == "active"))
    upcoming_count = _count(db, select(func.count()).select_from(Appointment).where(
        Appointment.status.in_(["scheduled", "confirmed"]), Appointment.ends_at >= current
    ))
    payment_attention = _count(db, select(func.count()).select_from(Order).where(
        Order.status.in_(["pending", "failed"])
    ))
    shared_reports = _count(db, select(func.count()).select_from(ProgressReport).where(
        ProgressReport.shared_with_patient.is_(True)
    ))
    completed_without_report = _count(db, select(func.count()).select_from(Appointment).where(
        Appointment.status == "completed",
        ~exists(select(ProgressReport.id).where(
            ProgressReport.patient_id == Appointment.patient_id,
            ProgressReport.created_at >= Appointment.ends_at,
        )),
    ))

    queue: list[dict] = []
    privacy_rows = db.scalars(select(DataRightsRequest).where(
        DataRightsRequest.status == "pending"
    ).order_by(DataRightsRequest.created_at.asc()).limit(queue_limit)).all()
    for row in privacy_rows:
        age = _age_seconds(row.created_at, current)
        queue.append({
            "id": f"privacy:{row.request_id}", "type": "privacy_request",
            "subject_ref": _ref("Request", row.request_id), "owner": "Privacy Team",
            "age_seconds": age, "priority": "high" if age >= 72 * 3600 else "medium",
            "action_url": "/admin/privacy",
        })

    unassigned_rows = db.scalars(select(PatientProfile).where(~active_assignment)
        .order_by(PatientProfile.created_at.asc()).limit(queue_limit)).all()
    for row in unassigned_rows:
        age = _age_seconds(row.created_at, current)
        queue.append({
            "id": f"assignment:{row.patient_id}", "type": "assignment",
            "subject_ref": _ref("Patient", row.patient_id), "owner": "Assignment Team",
            "age_seconds": age, "priority": "medium" if age >= 24 * 3600 else "low",
            "action_url": "/admin/assignments",
        })

    no_plan_rows = db.execute(select(PatientProfile, TherapistPatientAssignment.assigned_at).join(
        TherapistPatientAssignment,
        and_(
            TherapistPatientAssignment.patient_id == PatientProfile.patient_id,
            TherapistPatientAssignment.status == "active",
        ),
    ).where(~active_plan).order_by(TherapistPatientAssignment.assigned_at.asc()).limit(queue_limit)).all()
    for patient, assigned_at in no_plan_rows:
        age = _age_seconds(assigned_at, current)
        queue.append({
            "id": f"care_plan:{patient.patient_id}", "type": "care_plan",
            "subject_ref": _ref("Patient", patient.patient_id), "owner": "Care Operations",
            "age_seconds": age, "priority": "medium" if age >= 48 * 3600 else "low",
            "action_url": "/admin/assignments",
        })

    unpaid_rows = db.scalars(select(Appointment).where(
        Appointment.status.in_(["scheduled", "confirmed"]),
        Appointment.ends_at >= current,
        Appointment.payment_status.notin_(["paid", "refunded"]),
    ).order_by(Appointment.starts_at.asc()).limit(queue_limit)).all()
    for row in unpaid_rows:
        seconds_until = max(0, int((row.starts_at.replace(tzinfo=row.starts_at.tzinfo or timezone.utc) - current).total_seconds()))
        queue.append({
            "id": f"appointment:{row.appointment_id}", "type": "appointment",
            "subject_ref": _ref("Appointment", row.appointment_id), "owner": "Scheduling Team",
            "age_seconds": _age_seconds(row.created_at, current),
            "priority": "high" if seconds_until <= 24 * 3600 else "medium",
            "action_url": "/admin/appointments",
        })

    order_rows = db.scalars(select(Order).where(Order.status.in_(["pending", "failed"]))
        .order_by(Order.created_at.asc()).limit(queue_limit)).all()
    for row in order_rows:
        age = _age_seconds(row.created_at, current)
        if row.status == "pending" and age < 30 * 60:
            continue
        queue.append({
            "id": f"payment:{row.order_id}", "type": "payment",
            "subject_ref": _ref("Order", row.order_id), "owner": "Payments Team",
            "age_seconds": age, "priority": "high" if row.status == "failed" else "medium",
            "action_url": "/admin/payments",
        })

    if actor_user_id:
        recovery_alerts = db.scalars(select(Notification).where(
            Notification.user_id == actor_user_id,
            Notification.kind == PASSWORD_RESET_EMAIL_FAILED,
            Notification.read_at.is_(None),
        ).order_by(Notification.created_at.asc()).limit(queue_limit)).all()
        for row in recovery_alerts:
            target_user_id = (row.action_url or "").rsplit("/", 1)[-1] or None
            queue.append({
                "id": f"password_recovery:{row.notification_id}",
                "type": "password_recovery",
                "subject_ref": _ref("User", target_user_id),
                "owner": "Account Support",
                "age_seconds": _age_seconds(row.created_at, current),
                "priority": "high",
                "action_url": row.action_url or "/admin/users",
            })
    queue.sort(key=lambda item: (PRIORITY_RANK[item["priority"]], -item["age_seconds"], item["id"]))

    pending_privacy = _count(db, select(func.count()).select_from(DataRightsRequest).where(
        DataRightsRequest.status == "pending"
    ))
    privacy_by_type = {
        request_type: _count(db, select(func.count()).select_from(DataRightsRequest).where(
            DataRightsRequest.status == "pending", DataRightsRequest.request_type == request_type
        ))
        for request_type in ("export", "correction", "deletion")
    }
    recent_audit = db.scalars(select(AuditLog).order_by(AuditLog.created_at.desc()).limit(10)).all()

    return {
        "generated_at": current,
        "timezone": "Africa/Cairo",
        "metrics": {
            "users": users, "patients": patients, "active_assignments": assignments,
            "appointments": appointments, "paid_orders": paid_orders,
        },
        "stages": [
            _stage("account_consent", patients, missing_consent),
            _stage("therapist_assignment", assignments, unassigned),
            _stage("care_plan", active_plans, without_plan),
            _stage("appointment", upcoming_count, without_appointment),
            _stage("payment", paid_orders, payment_attention),
            _stage("follow_up", shared_reports, completed_without_report),
        ],
        "clinical_goals": [
            _clinical_goal("safety_boundaries", missing_consent + unassigned + without_plan),
            _clinical_goal("function_first", without_plan),
            _clinical_goal("adherence_confidence", without_appointment),
            _clinical_goal("therapist_review", len(queue)),
            _clinical_goal("measurement_quality", completed_without_report),
            _clinical_goal("equity_access", pending_privacy + payment_attention),
        ],
        "attention_queue": queue[:queue_limit],
        "today": {
            "date": local_now.date().isoformat(), "timezone": "Africa/Cairo",
            "appointments": _count(db, select(func.count()).select_from(Appointment).where(
                Appointment.starts_at >= utc_start, Appointment.starts_at < utc_end
            )),
        },
        "payment_exceptions": {
            "pending_orders": _count(db, select(func.count()).select_from(Order).where(Order.status == "pending")),
            "failed_payments": _count(db, select(func.count()).select_from(Payment).where(Payment.status == "failed")),
            "pending_refunds": _count(db, select(func.count()).select_from(Refund).where(Refund.status == "pending")),
        },
        "privacy_requests": {"pending": pending_privacy, **privacy_by_type},
        "recent_audit": [{
            "id": row.id, "actor_ref": _ref("User", row.actor_user_id), "action": row.action,
            "resource_type": row.resource_type, "resource_ref": _ref(row.resource_type.title(), row.resource_id),
            "created_at": row.created_at,
        } for row in recent_audit],
    }
