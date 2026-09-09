from concurrent.futures import ThreadPoolExecutor
from datetime import timedelta

import pytest
from fastapi import FastAPI
from fastapi.responses import JSONResponse
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session
from sqlalchemy.pool import StaticPool

from app.api.dependencies.auth import AuthError, get_current_user
from app.api.v1.connections import router
from app.db.database import get_db
from app.db.models import Base, User, PatientProfile, CareInvitation, TherapistPatientAssignment, AnalysisSession, AuditLog
from app.services import connection_service as service
from app.services.care_service import user_can_access_patient, user_can_access_session, accessible_session_filter
from app.api.routes.artifacts import authorize_artifact


def user(uid, role):
    return User(user_id=uid, username=uid, email=f"{uid}@example.com", full_name=uid,
                password_hash="test", role=role, is_active=True, is_verified=True, account_status="active")


@pytest.fixture
def db():
    engine = create_engine("sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool)
    Base.metadata.create_all(engine)
    with Session(engine, expire_on_commit=False) as db:
        db.add_all([user("therapist", "therapist"), user("therapist2", "therapist"), user("patient", "patient"), user("other", "patient"), user("admin", "admin"), user("support", "support")])
        db.add_all([PatientProfile(patient_id="p", user_id="patient", display_name="Patient"), PatientProfile(patient_id="other-p", user_id="other", display_name="Other"), PatientProfile(patient_id="legacy", display_name="Legacy")])
        db.commit()
        yield db
    engine.dispose()


def actor(db, uid):
    return db.scalar(select(User).where(User.user_id == uid))


def test_invitation_accept_multiple_disconnect_preserves_records(db):
    therapist, patient = actor(db, "therapist"), actor(db, "patient")
    invitation, token = service.invite(db, therapist, patient.email)
    db.commit()
    assert token not in invitation.token_hash
    assert not user_can_access_patient(db, therapist, "p")
    service.respond(db, patient, invitation.invitation_id, "accept", token)
    service.activate(db, "therapist2", "p", actor(db, "admin"), "admin", "Care team")
    db.commit()
    rows = db.scalars(select(TherapistPatientAssignment)).all()
    assert len(rows) == 2
    assert user_can_access_patient(db, therapist, "p")
    row = next(r for r in rows if r.therapist_user_id == "therapist")
    service.end_connection(db, patient, row.assignment_id, None)
    db.commit()
    assert not user_can_access_patient(db, therapist, "p")
    assert user_can_access_patient(db, actor(db, "therapist2"), "p")
    assert user_can_access_patient(db, patient, "p")
    assert db.scalar(select(PatientProfile).where(PatientProfile.patient_id == "p"))
    assert db.scalar(select(AuditLog).where(AuditLog.action == "connection.ended"))
    with pytest.raises(AuthError):
        service.respond(db, patient, invitation.invitation_id, "accept", token)


@pytest.mark.parametrize("failure", ["wrong_account", "unverified", "expired", "cancelled", "resend", "inactive_therapist"])
def test_invalid_invitation_never_activates(db, failure):
    therapist, patient = actor(db, "therapist"), actor(db, "patient")
    invitation, token = service.invite(db, therapist, patient.email)
    db.commit()
    if failure == "wrong_account": patient = actor(db, "other")
    if failure == "unverified": patient.is_verified = False
    if failure == "expired": invitation.expires_at = service.now() - timedelta(seconds=1)
    if failure == "cancelled": invitation.status, invitation.token_hash = "cancelled", None
    if failure == "inactive_therapist": therapist.account_status = "suspended"
    if failure == "resend": service.invite(db, therapist, patient.email, resend_id=invitation.invitation_id)
    db.commit()
    with pytest.raises(AuthError): service.respond(db, patient, invitation.invitation_id, "accept", token)
    assert not db.scalar(select(TherapistPatientAssignment))


def test_duplicate_retry_email_failure_and_reconnect(db, monkeypatch):
    therapist, patient = actor(db, "therapist"), actor(db, "patient")
    invitation, token = service.invite(db, therapist, patient.email)
    db.commit()
    same, duplicate_token = service.invite(db, therapist, patient.email)
    assert same.invitation_id == invitation.invitation_id and duplicate_token is None
    def fail_delivery(*args): raise service.EmailDeliveryError("unavailable")
    monkeypatch.setattr(service, "send_care_notification_email", fail_delivery)
    service.deliver_invitation(db, invitation, token)
    assert invitation.delivery_status == "failed"
    monkeypatch.setattr(service, "send_care_notification_email", lambda *args: None)
    invitation, replacement = service.invite(db, therapist, patient.email, resend_id=invitation.invitation_id)
    db.commit()
    service.deliver_invitation(db, invitation, replacement)
    assert invitation.delivery_status == "sent"
    service.respond(db, patient, invitation.invitation_id, "accept", replacement)
    db.commit()
    row = db.scalar(select(TherapistPatientAssignment))
    original_id = row.assignment_id
    service.end_connection(db, therapist, original_id, None)
    db.commit()
    reactivated = service.activate(db, therapist.user_id, "p", actor(db, "admin"), "admin", "Reconnected")
    db.commit()
    assert reactivated.assignment_id == original_id and reactivated.ended_at is None


def test_session_and_artifact_access_revoked_despite_creator_and_signature(db, monkeypatch):
    therapist = actor(db, "therapist")
    row = service.activate(db, therapist.user_id, "p", actor(db, "admin"), "admin", "Care")
    session = AnalysisSession(session_id="s", patient_id="p", owner_user_id=therapist.user_id,
                              created_by_user_id=therapist.user_id, exercise_id="squat", exercise_display_name="Squat", status="completed", report_id="report")
    db.add(session); db.commit()
    assert user_can_access_session(db, therapist, session)
    monkeypatch.setattr("app.api.routes.artifacts.valid_artifact_signature", lambda *args: True)
    authorize_artifact("report", "report", therapist, 9999999999, "valid", db)
    service.end_connection(db, actor(db, "patient"), row.assignment_id, None); db.commit()
    assert not user_can_access_session(db, therapist, session)
    assert not db.scalars(select(AnalysisSession).where(accessible_session_filter(therapist))).all()
    with pytest.raises(AuthError): authorize_artifact("report", "report", therapist, 9999999999, "valid", db)
    with pytest.raises(AuthError): authorize_artifact("report", "report", None, 9999999999, "valid", db)
    authorize_artifact("report", "report", actor(db, "patient"), None, None, db)


def test_legacy_no_blanket_access_and_support_denied(db):
    assert not user_can_access_patient(db, actor(db, "therapist"), "legacy")
    assert not user_can_access_patient(db, actor(db, "support"), "p")
    assert user_can_access_patient(db, actor(db, "admin"), "legacy")


def test_api_ownership_and_admin_reason(db):
    from app.api.v1.admin_platform import router as admin_router
    app = FastAPI()
    app.include_router(router); app.include_router(admin_router)
    @app.exception_handler(AuthError)
    async def handle(_request, exc): return JSONResponse(status_code=exc.status_code, content={"message": exc.message})
    app.dependency_overrides[get_db] = lambda: db
    app.dependency_overrides[get_current_user] = lambda: actor(db, "admin")
    with TestClient(app) as client:
        assert client.post("/api/v1/admin/assignments", json={"therapist_user_id": "therapist", "patient_id": "p"}).status_code == 422
        response = client.post("/api/v1/admin/assignments", json={"therapist_user_id": "therapist", "patient_id": "p", "reason": "Clinic intake"})
        assert response.status_code == 201
        aid = response.json()["assignment_id"]
        assert client.get("/api/v1/admin/assignment-options?unassigned=true").json()["patients"] == [{"patient_id": "legacy", "name": "Legacy"}, {"patient_id": "other-p", "name": "Other"}]
        app.dependency_overrides[get_current_user] = lambda: actor(db, "other")
        assert client.post(f"/api/v1/connections/{aid}/end", json={}).status_code == 403
        assert client.get("/api/v1/connections").json() == []


def test_concurrent_admin_activation_has_one_assignment(tmp_path):
    engine = create_engine(f"sqlite:///{tmp_path / 'concurrent.db'}", connect_args={"timeout": 15})
    Base.metadata.create_all(engine)
    with Session(engine) as db:
        db.add_all([user("t", "therapist"), user("p", "patient"), user("a", "admin"), PatientProfile(patient_id="p", user_id="p", display_name="Patient")]); db.commit()
    def activate(_):
        with Session(engine) as db:
            row = service.activate(db, "t", "p", actor(db, "a"), "admin", "Intake")
            db.commit()
            return row.assignment_id
    with ThreadPoolExecutor(max_workers=2) as pool:
        ids = list(pool.map(activate, range(2)))
    assert ids[0] == ids[1]
    engine.dispose()


def test_disconnection_blocks_queued_clinical_email(db, monkeypatch):
    from app.services.care_service import create_notification
    from app.services.notification_service import deliver_pending_emails, notification_accessible
    therapist = actor(db, "therapist")
    connection = service.activate(db, therapist.user_id, "p", actor(db, "admin"), "admin", "Care")
    note = create_notification(db, therapist.user_id, "exercise_response_follow_up", "Review", "Clinical details", "/therapist/patients/p")
    note.email_required = True
    db.commit()
    service.end_connection(db, actor(db, "patient"), connection.assignment_id, None); db.commit()
    assert not notification_accessible(db, note, therapist)
    delivered = []
    monkeypatch.setattr("app.services.notification_service.send_care_notification_email", lambda email, title, body, url: delivered.append(body))
    deliver_pending_emails(db)
    assert "Clinical details" not in delivered
    assert not note.email_required


def test_multiple_therapist_plans_remain_active_and_attributed(db):
    from app.db.crud import create_exercise_plan
    from app.db.models import ExercisePlan
    from app.schemas.patient_schema import ExercisePlanCreate, ExercisePlanItemCreate
    from app.services.care_service import patient_today
    from datetime import date
    data = ExercisePlanCreate(title="Plan", items=[ExercisePlanItemCreate(exercise_id="knee_extension", sets=2, reps=5, days_per_week=3)])
    first = create_exercise_plan(db, "p", data, "therapist")
    second = create_exercise_plan(db, "p", data, "therapist2")
    replacement = create_exercise_plan(db, "p", data, "therapist")
    db.refresh(first); db.refresh(second)
    assert first.status == "paused" and second.status == "active"
    today = patient_today(db, db.scalar(select(PatientProfile).where(PatientProfile.patient_id == "p")), date.today())
    assert len(today.plan_items) == 2
    assert {item.created_by_name for item in today.plan_items} == {"therapist", "therapist2"}


def test_ended_appointment_is_retained_flagged_and_not_joinable(db):
    from app.db.models import Appointment, Notification
    from app.api.v1.scheduling import join
    from app.services.notification_service import enqueue_due_appointment_reminders
    therapist = actor(db, "therapist")
    connection = service.activate(db, therapist.user_id, "p", actor(db, "admin"), "admin", "Intake")
    start = service.now() + timedelta(hours=24)
    db.add(Appointment(appointment_id="appointment", therapist_user_id=therapist.user_id, patient_id="p", starts_at=start, ends_at=start + timedelta(minutes=30), created_by_user_id="admin"))
    db.commit()
    service.end_connection(db, actor(db, "patient"), connection.assignment_id, None); db.commit()
    assert service.summary(db, connection)["appointments_needing_review"] == 1
    assert db.scalar(select(Appointment)).status == "scheduled"
    assert join("appointment", therapist, db).status_code == 403
    assert enqueue_due_appointment_reminders(db) == 0
    assert db.scalar(select(Notification).where(Notification.kind == "connection_appointment_review"))


def test_job_result_cannot_bypass_ended_assignment(db, monkeypatch):
    from app.db.models import AnalysisJob
    from app.services.analysis_job_service import get_owned_job
    from sqlalchemy.orm import sessionmaker
    therapist = actor(db, "therapist")
    row = service.activate(db, therapist.user_id, "p", actor(db, "admin"), "admin", "Care")
    db.add(AnalysisJob(job_id="job", owner_user_id=therapist.user_id, exercise_id="squat", source_path="fixture.mp4", source_filename="fixture.mp4", options_json='{"patient_id":"p"}', status="completed"))
    db.commit()
    monkeypatch.setattr("app.services.analysis_job_service.SessionLocal", sessionmaker(bind=db.bind))
    assert get_owned_job("job", therapist)
    service.end_connection(db, actor(db, "patient"), row.assignment_id, None); db.commit()
    assert get_owned_job("job", therapist) is None
