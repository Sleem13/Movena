"""Care-platform domain services with explicit patient and therapist ownership."""

from __future__ import annotations

import json
import hashlib
from datetime import date, datetime, timedelta, timezone
from statistics import mean
from uuid import uuid4

from sqlalchemy import and_, func, or_, select, text
from sqlalchemy.orm import Session, selectinload

from app.core.config import get_settings
from app.db.models import (
    AdherenceEntry, AnalysisSession, Appointment, AuditLog, ExercisePlan, ExercisePlanItem,
    Notification, PatientProfile, TherapistPatientAssignment, User, utc_now,
)
from app.schemas.auth_schema import UserRole
from app.schemas.care_schema import (
    AdherenceCreate, AdherenceDetail, AppointmentCreate, AppointmentSummary,
    CarePlanItem, ExerciseResponseReview, NotificationSummary, PatientTodayResponse,
)


EXERCISE_RESPONSE_OK = (
    "Continue only as prescribed. This check-in does not authorize exercise progression; "
    "contact your treating clinician if symptoms change or you are unsure."
)
EXERCISE_RESPONSE_FOLLOW_UP = (
    "Do not progress this exercise. Pause or use only the modification already provided by your clinician, "
    "and contact your treating clinician for review. Seek appropriate urgent help for severe or concerning symptoms."
)


def audit_event(
    db: Session, actor_user_id: str | None, action: str, resource_type: str,
    resource_id: str | None, metadata: dict | None = None,
) -> None:
    db.add(AuditLog(
        actor_user_id=actor_user_id,
        action=action,
        resource_type=resource_type,
        resource_id=resource_id,
        metadata_json=json.dumps(metadata or {}, sort_keys=True),
    ))


def patient_for_user(db: Session, user_id: str) -> PatientProfile | None:
    return db.scalar(select(PatientProfile).where(PatientProfile.user_id == user_id))


def therapist_can_access_patient(db: Session, therapist_user_id: str, patient_id: str) -> bool:
    return db.scalar(select(TherapistPatientAssignment.id).where(
        TherapistPatientAssignment.therapist_user_id == therapist_user_id,
        TherapistPatientAssignment.patient_id == patient_id,
        TherapistPatientAssignment.status == "active",
    )) is not None


def user_can_access_patient(db: Session, user: User, patient_id: str) -> bool:
    if user.role in {UserRole.super_admin.value, UserRole.admin.value}:
        return True
    if user.role == UserRole.therapist.value:
        if therapist_can_access_patient(db, user.user_id, patient_id):
            return True
        # Preserve access to pre-account demo records only. Real patient
        # accounts always require an explicit active assignment.
        legacy_profile = db.scalar(select(PatientProfile).where(
            PatientProfile.patient_id == patient_id,
            PatientProfile.user_id.is_(None),
        ))
        return legacy_profile is not None
    if user.role == UserRole.patient.value:
        profile = patient_for_user(db, user.user_id)
        return profile is not None and profile.patient_id == patient_id
    return False


def list_patients_for_therapist(db: Session, actor: User) -> list[PatientProfile]:
    statement = select(PatientProfile).order_by(PatientProfile.created_at.desc())
    if actor.role == UserRole.therapist.value:
        statement = statement.join(
            TherapistPatientAssignment,
            TherapistPatientAssignment.patient_id == PatientProfile.patient_id,
        ).where(
            TherapistPatientAssignment.therapist_user_id == actor.user_id,
            TherapistPatientAssignment.status == "active",
        )
    return list(db.scalars(statement).all())


def ensure_assignment(
    db: Session, therapist_user_id: str, patient_id: str, assigned_by_user_id: str | None,
) -> TherapistPatientAssignment:
    row = db.scalar(select(TherapistPatientAssignment).where(
        TherapistPatientAssignment.therapist_user_id == therapist_user_id,
        TherapistPatientAssignment.patient_id == patient_id,
    ))
    if row is None:
        row = TherapistPatientAssignment(
            assignment_id=str(uuid4()), therapist_user_id=therapist_user_id,
            patient_id=patient_id, assigned_by_user_id=assigned_by_user_id,
        )
        db.add(row)
    else:
        row.status = "active"
        row.assigned_by_user_id = assigned_by_user_id
    return row


def create_notification(
    db: Session, user_id: str, kind: str, title: str, body: str,
    action_url: str | None = None, dedup_key: str | None = None,
) -> Notification:
    if dedup_key:
        existing = db.scalar(select(Notification).where(Notification.dedup_key == dedup_key))
        if existing:
            return existing
    row = Notification(
        notification_id=str(uuid4()), user_id=user_id, kind=kind, title=title,
        body=body, action_url=action_url, dedup_key=dedup_key,
    )
    db.add(row)
    return row


def notification_summary(row: Notification) -> NotificationSummary:
    return NotificationSummary(
        notification_id=row.notification_id, kind=row.kind, title=row.title,
        body=row.body, action_url=row.action_url, read_at=row.read_at,
        created_at=row.created_at,
    )


def appointment_summary(row: Appointment, now: datetime | None = None) -> AppointmentSummary:
    current = now or datetime.now(timezone.utc)
    starts = row.starts_at if row.starts_at.tzinfo else row.starts_at.replace(tzinfo=timezone.utc)
    ends = row.ends_at if row.ends_at.tzinfo else row.ends_at.replace(tzinfo=timezone.utc)
    return AppointmentSummary(
        appointment_id=row.appointment_id, patient_id=row.patient_id,
        therapist_user_id=row.therapist_user_id, starts_at=row.starts_at,
        ends_at=row.ends_at, status=row.status, delivery_mode=row.delivery_mode,
        payment_status=row.payment_status,
        can_join=row.status in {"scheduled", "confirmed"}
        and starts - timedelta(minutes=15) <= current <= ends + timedelta(minutes=30),
    )


def patient_today(db: Session, patient: PatientProfile, day: date) -> PatientTodayResponse:
    plan = db.scalar(select(ExercisePlan).where(
        ExercisePlan.patient_id == patient.patient_id,
        ExercisePlan.status == "active",
        or_(ExercisePlan.start_date.is_(None), func.date(ExercisePlan.start_date) <= day),
        or_(ExercisePlan.end_date.is_(None), func.date(ExercisePlan.end_date) >= day),
    ).options(selectinload(ExercisePlan.items)).order_by(ExercisePlan.created_at.desc()))
    entries = {
        row.plan_item_id: row
        for row in db.scalars(select(AdherenceEntry).where(
            AdherenceEntry.patient_id == patient.patient_id,
            AdherenceEntry.scheduled_date == day,
        )).all()
    }
    items: list[CarePlanItem] = []
    for item in plan.items if plan else []:
        try:
            schedule_days = json.loads(item.schedule_days_json or "[]")
        except json.JSONDecodeError:
            schedule_days = []
        if schedule_days and day.weekday() not in schedule_days:
            continue
        entry = entries.get(item.item_id)
        items.append(CarePlanItem(
            item_id=item.item_id, exercise_id=item.exercise_id, sets=item.sets,
            reps=item.reps, duration_minutes=item.duration_minutes,
            rest_interval_seconds=item.rest_interval_seconds, tempo=item.tempo,
            instructions=item.instructions, precautions=item.precautions,
            target_rom_degrees=item.target_rom_degrees, target_score=item.target_score,
            requested_media_upload=item.requested_media_upload,
            requires_ai_analysis=item.requires_ai_analysis,
            completion_status=entry.completion_status if entry else None,
            pain_before=entry.pain_before if entry else None,
            pain_after=entry.pain_after if entry else None,
            difficulty=entry.difficulty if entry else None,
            fatigue=entry.fatigue if entry else None,
            perceived_exertion=entry.perceived_exertion if entry else None,
            symptoms_changed=entry.symptoms_changed if entry else False,
            stopped_due_to_symptoms=entry.stopped_due_to_symptoms if entry else False,
            symptom_flags=json.loads(entry.symptom_flags_json or "[]") if entry else [],
            response_state=entry.response_state if entry else "not_assessed",
            supportive_instruction=entry.supportive_instruction if entry else None,
            clinician_review_required=entry.clinician_review_required if entry else False,
            reviewed_at=entry.reviewed_at if entry else None,
            patient_comment=entry.note if entry else None,
            analysis_session_id=entry.analysis_session_id if entry else None,
        ))
    now = datetime.now(timezone.utc)
    upcoming = db.scalar(select(Appointment).where(
        Appointment.patient_id == patient.patient_id,
        Appointment.status.in_(["scheduled", "confirmed"]),
        Appointment.ends_at >= now,
    ).order_by(Appointment.starts_at.asc()))
    week_start = day - timedelta(days=6)
    recent = list(db.scalars(select(AdherenceEntry).where(
        AdherenceEntry.patient_id == patient.patient_id,
        AdherenceEntry.scheduled_date.between(week_start, day),
    )).all())
    completed_count = sum(row.completion_status == "completed" for row in recent)
    partial_count = sum(row.completion_status == "partial" for row in recent)
    missed_count = sum(row.completion_status == "not_completed" for row in recent)
    completed = completed_count + partial_count
    pain_values = [row.pain_after for row in recent if row.pain_after is not None]
    unread = db.scalar(select(func.count()).select_from(Notification).where(
        Notification.user_id == patient.user_id, Notification.read_at.is_(None)
    )) if patient.user_id else 0
    return PatientTodayResponse(
        patient_id=patient.patient_id, date=day, plan_title=plan.title if plan else None,
        plan_items=items, upcoming_appointment=appointment_summary(upcoming) if upcoming else None,
        unread_notifications=int(unread or 0),
        adherence_percent_7d=round(completed / len(recent) * 100, 1) if recent else None,
        average_pain_7d=round(mean(pain_values), 1) if pain_values else None,
        completed_count_7d=completed_count, partial_count_7d=partial_count,
        missed_count_7d=missed_count,
    )


def record_adherence(
    db: Session, patient: PatientProfile, data: AdherenceCreate,
    idempotency_key: str | None,
) -> AdherenceDetail:
    item = db.scalar(select(ExercisePlanItem).join(
        ExercisePlan, ExercisePlan.plan_id == ExercisePlanItem.plan_id,
    ).where(
        ExercisePlanItem.item_id == data.plan_item_id,
        ExercisePlan.patient_id == patient.patient_id,
    ))
    if item is None:
        raise LookupError("PLAN_ITEM_NOT_FOUND")
    row = None
    scoped_key = hashlib.sha256(f"{patient.patient_id}:{idempotency_key}".encode()).hexdigest() if idempotency_key else None
    if idempotency_key:
        row = db.scalar(select(AdherenceEntry).where(
            AdherenceEntry.idempotency_key == scoped_key,
            AdherenceEntry.patient_id == patient.patient_id,
        ))
    if row is None:
        row = db.scalar(select(AdherenceEntry).where(
            AdherenceEntry.patient_id == patient.patient_id,
            AdherenceEntry.plan_item_id == data.plan_item_id,
            AdherenceEntry.scheduled_date == data.scheduled_date,
        ))
    if row is None:
        row = AdherenceEntry(
            adherence_id=str(uuid4()), patient_id=patient.patient_id,
            plan_item_id=data.plan_item_id, scheduled_date=data.scheduled_date,
            completion_status=data.completion_status, idempotency_key=scoped_key,
        )
        db.add(row)
    linked_session = None
    if data.analysis_session_id:
        linked_session = db.scalar(select(AnalysisSession).where(
            AnalysisSession.session_id == data.analysis_session_id,
            or_(
                AnalysisSession.patient_id == patient.patient_id,
                AnalysisSession.owner_user_id == patient.user_id,
            ),
        ))
        if linked_session is None:
            raise ValueError("ANALYSIS_SESSION_ACCESS_DENIED")
        if linked_session.exercise_id != item.exercise_id:
            raise ValueError("ANALYSIS_EXERCISE_MISMATCH")
    previous_response = (
        row.pain_before, row.pain_after, row.difficulty, row.fatigue,
        row.perceived_exertion, row.symptoms_changed, row.stopped_due_to_symptoms,
        row.symptom_flags_json,
    )
    previous_reviewed_at = row.reviewed_at
    submitted_response = (
        data.pain_before, data.pain_after, data.difficulty, data.fatigue,
        data.perceived_exertion, data.symptoms_changed, data.stopped_due_to_symptoms,
        json.dumps(data.symptom_flags),
    )
    if row.clinician_review_required and submitted_response != previous_response:
        raise ValueError("CLINICAL_REVIEW_PENDING")
    for field in (
        "completion_status", "pain_before", "pain_after", "difficulty", "fatigue",
        "perceived_exertion", "symptoms_changed", "stopped_due_to_symptoms", "note",
    ):
        setattr(row, field, getattr(data, field))
    row.symptom_flags_json = json.dumps(data.symptom_flags)
    if data.analysis_session_id is not None:
        row.analysis_session_id = data.analysis_session_id
    if linked_session is not None:
        linked_session.patient_id = patient.patient_id
        linked_session.plan_item_id = item.item_id
    row.completed_at = utc_now() if data.completion_status in {"completed", "partial"} else None
    settings = get_settings()
    alert = bool(
        (data.pain_after is not None and data.pain_after >= settings.high_pain_threshold)
        or (
            data.pain_before is not None and data.pain_after is not None
            and data.pain_after - data.pain_before >= settings.pain_increase_threshold
        )
    )
    follow_up = bool(
        alert or data.symptoms_changed or data.stopped_due_to_symptoms
        or data.symptom_flags or (data.perceived_exertion is not None and data.perceived_exertion >= 9)
    )
    row.response_state = "clinical_follow_up" if follow_up else "within_reported_tolerance"
    row.supportive_instruction = EXERCISE_RESPONSE_FOLLOW_UP if follow_up else EXERCISE_RESPONSE_OK
    current_response = (
        row.pain_before, row.pain_after, row.difficulty, row.fatigue,
        row.perceived_exertion, row.symptoms_changed, row.stopped_due_to_symptoms,
        row.symptom_flags_json,
    )
    if follow_up and current_response != previous_response:
        row.reviewed_at = None
        row.reviewed_by_user_id = None
        row.review_disposition = None
        row.review_note = None
    row.clinician_review_required = follow_up and row.reviewed_at is None
    if follow_up:
        therapist_ids = db.scalars(select(TherapistPatientAssignment.therapist_user_id).where(
            TherapistPatientAssignment.patient_id == patient.patient_id,
            TherapistPatientAssignment.status == "active",
        )).all()
        for therapist_id in therapist_ids:
            review_cycle = previous_reviewed_at.isoformat() if previous_reviewed_at else "initial"
            create_notification(
                db, therapist_id, "exercise_response_follow_up", "Exercise response review needed",
                f"{patient.display_name} recorded an exercise response that needs professional review.",
                action_url=f"/therapist?patient={patient.patient_id}",
                dedup_key=f"exercise-response:{patient.patient_id}:{data.plan_item_id}:{data.scheduled_date}:{review_cycle}",
            )
    audit_event(db, patient.user_id, "adherence.recorded", "adherence", row.adherence_id, {
        "patient_id": patient.patient_id, "plan_item_id": data.plan_item_id,
        "scheduled_date": data.scheduled_date.isoformat(), "alert_created": follow_up,
        "response_state": row.response_state, "symptoms_changed": data.symptoms_changed,
        "stopped_due_to_symptoms": data.stopped_due_to_symptoms,
    })
    db.commit()
    db.refresh(row)
    return AdherenceDetail(
        adherence_id=row.adherence_id, patient_id=row.patient_id,
        plan_item_id=row.plan_item_id, scheduled_date=row.scheduled_date,
        completion_status=row.completion_status, pain_before=row.pain_before,
        pain_after=row.pain_after, difficulty=row.difficulty, note=row.note,
        fatigue=row.fatigue, perceived_exertion=row.perceived_exertion,
        symptoms_changed=row.symptoms_changed,
        stopped_due_to_symptoms=row.stopped_due_to_symptoms,
        symptom_flags=json.loads(row.symptom_flags_json or "[]"),
        safety_acknowledged=data.safety_acknowledged,
        analysis_session_id=row.analysis_session_id,
        alert_created=follow_up, response_state=row.response_state,
        supportive_instruction=row.supportive_instruction or EXERCISE_RESPONSE_OK,
        clinician_review_required=row.clinician_review_required,
        reviewed_at=row.reviewed_at, reviewed_by_user_id=row.reviewed_by_user_id,
        review_disposition=row.review_disposition, review_note=row.review_note,
        created_at=row.created_at, updated_at=row.updated_at,
    )


def acknowledge_exercise_response(
    db: Session, actor: User, row: AdherenceEntry, data: ExerciseResponseReview,
) -> AdherenceEntry:
    if not row.clinician_review_required or row.response_state != "clinical_follow_up":
        raise ValueError("REVIEW_NOT_REQUIRED")
    row.reviewed_at = utc_now()
    row.reviewed_by_user_id = actor.user_id
    row.review_disposition = data.disposition
    row.review_note = data.note
    row.clinician_review_required = False
    audit_event(db, actor.user_id, "exercise_response.reviewed", "adherence_entry", row.adherence_id, {
        "patient_id": row.patient_id,
        "disposition": data.disposition,
        "clinician_attestation": True,
    })
    db.commit()
    db.refresh(row)
    return row


def create_appointment(
    db: Session, data: AppointmentCreate, actor_user_id: str,
    idempotency_key: str | None,
) -> Appointment:
    scoped_key = hashlib.sha256(f"{actor_user_id}:{idempotency_key}".encode()).hexdigest() if idempotency_key else None
    if scoped_key:
        existing = db.scalar(select(Appointment).where(
            Appointment.idempotency_key == scoped_key,
            Appointment.created_by_user_id == actor_user_id,
        ))
        if existing:
            return existing
    starts = data.starts_at.astimezone(timezone.utc)
    ends = data.ends_at.astimezone(timezone.utc)
    if db.bind is not None and db.bind.dialect.name == "postgresql":
        db.execute(text("SELECT pg_advisory_xact_lock(hashtext(:therapist_id))"), {
            "therapist_id": data.therapist_user_id,
        })
    overlap = db.scalar(select(Appointment.id).where(
        Appointment.therapist_user_id == data.therapist_user_id,
        Appointment.status.in_(["scheduled", "confirmed"]),
        Appointment.starts_at < ends,
        Appointment.ends_at > starts,
    ).with_for_update())
    if overlap is not None:
        raise ValueError("APPOINTMENT_CONFLICT")
    row = Appointment(
        appointment_id=str(uuid4()), patient_id=data.patient_id,
        therapist_user_id=data.therapist_user_id, service_id=data.service_id,
        starts_at=starts, ends_at=ends, delivery_mode=data.delivery_mode,
        status="scheduled", created_by_user_id=actor_user_id,
        idempotency_key=scoped_key,
    )
    db.add(row)
    patient = db.scalar(select(PatientProfile).where(PatientProfile.patient_id == data.patient_id))
    if patient and patient.user_id:
        create_notification(
            db, patient.user_id, "appointment_booked", "Appointment booked",
            f"Your appointment is scheduled for {starts.isoformat()}.",
            action_url="/appointments", dedup_key=f"appointment:{row.appointment_id}:booked",
        )
    create_notification(
        db, data.therapist_user_id, "appointment_booked", "New appointment",
        f"A patient appointment is scheduled for {starts.isoformat()}.",
        action_url="/therapist", dedup_key=f"appointment:{row.appointment_id}:therapist",
    )
    audit_event(db, actor_user_id, "appointment.created", "appointment", row.appointment_id, {
        "patient_id": data.patient_id, "therapist_user_id": data.therapist_user_id,
        "starts_at": starts.isoformat(),
    })
    db.commit()
    db.refresh(row)
    return row
