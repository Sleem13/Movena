import hashlib
import hmac
from datetime import date

import pytest
from pydantic import ValidationError
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from sqlalchemy.pool import StaticPool

from app.db.crud import create_exercise_plan
from app.db.models import (
    AdherenceEntry, AnalysisSession, AuditLog, Base, ExercisePlan, Notification,
    PatientProfile, TherapistPatientAssignment, User,
)
from app.schemas.care_schema import AdherenceCreate, CheckoutCreate, ExerciseResponseReview
from app.schemas.patient_schema import ExercisePlanCreate, ExercisePlanItemCreate
from app.services.care_service import (
    acknowledge_exercise_response, patient_today, record_adherence, user_can_access_patient,
)
from app.services.paymob_service import HMAC_FIELDS, _nested, verify_webhook_hmac


@pytest.fixture
def care_db():
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(engine)
    with Session(engine) as session:
        yield session
    engine.dispose()


def _user(user_id: str, role: str) -> User:
    return User(
        user_id=user_id,
        username=user_id,
        email=f"{user_id}@example.test",
        password_hash="test-only",
        role=role,
        is_active=True,
        is_verified=True,
    )


def test_patient_access_requires_identity_or_active_assignment(care_db: Session):
    patient_user = _user("patient-user", "patient")
    assigned_therapist = _user("assigned-therapist", "therapist")
    other_therapist = _user("other-therapist", "therapist")
    support_user = _user("support-user", "support")
    profile = PatientProfile(
        patient_id="patient-profile",
        user_id=patient_user.user_id,
        display_name="Test Patient",
    )
    care_db.add_all([patient_user, assigned_therapist, other_therapist, support_user, profile])
    care_db.flush()

    assert user_can_access_patient(care_db, patient_user, profile.patient_id)
    assert not user_can_access_patient(care_db, other_therapist, profile.patient_id)
    assert not user_can_access_patient(care_db, support_user, profile.patient_id)

    care_db.add(TherapistPatientAssignment(
        assignment_id="assignment-1",
        therapist_user_id=assigned_therapist.user_id,
        patient_id=profile.patient_id,
        status="active",
    ))
    care_db.flush()

    assert user_can_access_patient(care_db, assigned_therapist, profile.patient_id)


def test_checkout_requires_one_product_and_egyptian_phone():
    valid = CheckoutCreate(service_id="service-1", billing_phone="+201012345678")
    assert valid.service_id == "service-1"

    with pytest.raises(ValidationError):
        CheckoutCreate(service_id="service-1", package_id="package-1", billing_phone="+201012345678")
    with pytest.raises(ValidationError):
        CheckoutCreate(service_id="service-1", billing_phone="01012345678")


def test_paymob_webhook_hmac_rejects_tampering():
    payload = {
        "amount_cents": 12500,
        "created_at": "2026-08-28T12:00:00Z",
        "currency": "EGP",
        "id": 123456,
        "order": {"id": 98765},
        "source_data": {"pan": "2345", "sub_type": "MasterCard", "type": "card"},
        "success": True,
    }
    secret = "test-paymob-hmac-secret"
    message = "".join(str(_nested(payload, field)) for field in HMAC_FIELDS)
    signature = hmac.new(secret.encode(), message.encode(), hashlib.sha512).hexdigest()

    assert verify_webhook_hmac(payload, signature, secret)
    payload["amount_cents"] = 13000
    assert not verify_webhook_hmac(payload, signature, secret)


def test_rehab_check_in_links_owned_matching_analysis_and_surfaces_outcomes(care_db: Session):
    patient_user = _user("phase1-patient", "patient")
    profile = PatientProfile(patient_id="phase1-profile", user_id=patient_user.user_id, display_name="Phase One")
    care_db.add_all([patient_user, profile]); care_db.commit()
    plan = create_exercise_plan(care_db, profile.patient_id, ExercisePlanCreate(
        title="Knee recovery",
        items=[ExercisePlanItemCreate(
            exercise_id="knee_extension", sets=3, reps=10, days_per_week=5,
            schedule_days=[0, 1, 2, 3, 4], rest_interval_seconds=60,
            tempo="3-1-3", target_rom_degrees=90, target_score=80,
            requested_media_upload=True, requires_ai_analysis=True,
        )],
    ), "therapist-1")
    item = plan.items[0]
    analysis = AnalysisSession(
        session_id="phase1-session", owner_user_id=patient_user.user_id,
        exercise_id="knee_extension", exercise_display_name="Knee Extension", status="completed",
    )
    care_db.add(analysis); care_db.commit()

    result = record_adherence(care_db, profile, AdherenceCreate(
        plan_item_id=item.item_id, scheduled_date=date(2026, 8, 28),
        completion_status="completed", pain_before=4, pain_after=3,
        difficulty=2, fatigue=3, note="Controlled return felt easier.",
        analysis_session_id=analysis.session_id,
    ), "phase1-idempotency")

    assert result.fatigue == 3
    assert result.analysis_session_id == analysis.session_id
    assert analysis.patient_id == profile.patient_id
    assert analysis.plan_item_id == item.item_id
    snapshot = patient_today(care_db, profile, date(2026, 8, 28))
    assert snapshot.plan_items[0].rest_interval_seconds == 60
    assert snapshot.plan_items[0].requires_ai_analysis is True
    assert snapshot.plan_items[0].fatigue == 3
    assert snapshot.plan_items[0].patient_comment == "Controlled return felt easier."


def test_rehab_analysis_link_rejects_wrong_exercise_and_new_plan_preserves_history(care_db: Session):
    patient_user = _user("history-patient", "patient")
    profile = PatientProfile(patient_id="history-profile", user_id=patient_user.user_id, display_name="History Patient")
    care_db.add_all([patient_user, profile]); care_db.commit()
    first = create_exercise_plan(care_db, profile.patient_id, ExercisePlanCreate(
        title="Version one", items=[ExercisePlanItemCreate(exercise_id="knee_extension", sets=3, reps=8, days_per_week=3)],
    ), "therapist-1")
    second = create_exercise_plan(care_db, profile.patient_id, ExercisePlanCreate(
        title="Version two", items=[ExercisePlanItemCreate(exercise_id="sit_to_stand", sets=2, reps=6, days_per_week=4)],
    ), "therapist-1")
    care_db.add(AnalysisSession(
        session_id="wrong-exercise", owner_user_id=patient_user.user_id,
        exercise_id="knee_extension", exercise_display_name="Knee Extension", status="completed",
    )); care_db.commit()

    with pytest.raises(ValueError, match="ANALYSIS_EXERCISE_MISMATCH"):
        record_adherence(care_db, profile, AdherenceCreate(
            plan_item_id=second.items[0].item_id, scheduled_date=date(2026, 8, 29),
            completion_status="partial", analysis_session_id="wrong-exercise",
        ), None)

    assert care_db.get(ExercisePlan, first.id).status == "paused"
    assert care_db.get(ExercisePlan, second.id).status == "active"


def test_exercise_response_requires_acknowledgement_and_closes_clinical_review_loop(care_db: Session):
    patient_user = _user("response-patient", "patient")
    therapist = _user("response-therapist", "therapist")
    profile = PatientProfile(
        patient_id="response-profile", user_id=patient_user.user_id,
        display_name="Response Patient",
    )
    care_db.add_all([patient_user, therapist, profile])
    care_db.flush()
    care_db.add(TherapistPatientAssignment(
        assignment_id="response-assignment", therapist_user_id=therapist.user_id,
        patient_id=profile.patient_id, status="active",
    ))
    care_db.commit()
    plan = create_exercise_plan(care_db, profile.patient_id, ExercisePlanCreate(
        title="Graded activity",
        items=[ExercisePlanItemCreate(
            exercise_id="sit_to_stand", sets=2, reps=6, days_per_week=3,
        )],
    ), therapist.user_id)

    with pytest.raises(ValidationError, match="Safety acknowledgement"):
        AdherenceCreate(
            plan_item_id=plan.items[0].item_id, scheduled_date=date(2026, 8, 31),
            completion_status="partial", symptoms_changed=True,
        )

    result = record_adherence(care_db, profile, AdherenceCreate(
        plan_item_id=plan.items[0].item_id, scheduled_date=date(2026, 8, 31),
        completion_status="partial", pain_before=2, pain_after=5,
        perceived_exertion=9, symptoms_changed=True,
        stopped_due_to_symptoms=True, symptom_flags=["dizziness"],
        safety_acknowledged=True,
    ), "response-check-in")

    assert result.response_state == "clinical_follow_up"
    assert result.clinician_review_required is True
    assert "Do not progress" in result.supportive_instruction
    notification = care_db.query(Notification).filter_by(
        user_id=therapist.user_id, kind="exercise_response_follow_up",
    ).one()
    assert "review" in notification.title.lower()

    with pytest.raises(ValueError, match="CLINICAL_REVIEW_PENDING"):
        record_adherence(care_db, profile, AdherenceCreate(
            plan_item_id=plan.items[0].item_id, scheduled_date=date(2026, 8, 31),
            completion_status="completed", pain_before=0, pain_after=0,
            perceived_exertion=2,
        ), None)

    row = care_db.query(AdherenceEntry).filter_by(adherence_id=result.adherence_id).one()
    reviewed = acknowledge_exercise_response(care_db, therapist, row, ExerciseResponseReview(
        disposition="contacted_patient", note="Reviewed symptoms and arranged follow-up.",
        clinician_attestation=True,
    ))
    assert reviewed.clinician_review_required is False
    assert reviewed.reviewed_by_user_id == therapist.user_id
    assert care_db.query(AuditLog).filter_by(
        action="exercise_response.reviewed", resource_id=row.adherence_id,
    ).one().metadata_json
