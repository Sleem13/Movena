from datetime import date, timedelta

from fastapi.testclient import TestClient
from sqlalchemy import select
from sqlalchemy.orm import sessionmaker

from app.core.security import create_access_token, get_password_hash
from app.db.database import Base, create_database_engine, get_db
from app.db.models import (
    AuditLog, Notification, PatientProfile, TherapistPatientAssignment, User,
)
from app.main import app


def _setup(tmp_path):
    engine = create_database_engine(f"sqlite:///{(tmp_path / 'coaching.db').as_posix()}")
    Base.metadata.create_all(engine)
    factory = sessionmaker(bind=engine, expire_on_commit=False)
    with factory() as db:
        db.add_all([
            User(user_id="patient-1", email="patient@example.com", password_hash=get_password_hash("Password123!"), role="patient", is_verified=True),
            User(user_id="patient-2", email="other@example.com", password_hash=get_password_hash("Password123!"), role="patient", is_verified=True),
            User(user_id="therapist-1", email="therapist@example.com", password_hash=get_password_hash("Password123!"), role="therapist", is_verified=True),
        ])
        db.add_all([
            PatientProfile(patient_id="profile-1", user_id="patient-1", display_name="Patient One"),
            PatientProfile(patient_id="profile-2", user_id="patient-2", display_name="Patient Two"),
        ])
        db.add(TherapistPatientAssignment(
            assignment_id="assignment-1", therapist_user_id="therapist-1",
            patient_id="profile-1", status="active", assigned_by_user_id="therapist-1",
        ))
        db.commit()

    def override():
        session = factory()
        try:
            yield session
        finally:
            session.close()

    app.dependency_overrides[get_db] = override
    return TestClient(app), factory


def _headers(user_id, role):
    return {"Authorization": f"Bearer {create_access_token(user_id, role)}"}


GOAL = {
    "domain": "activity",
    "title": "Build a consistent walking routine",
    "specific_action": "Walk for ten minutes after lunch on planned days",
    "measurement": "Three completed walks each week",
    "why_important": "Return to community activities with confidence",
    "target_date": "2026-12-31",
    "confidence": 4,
    "patient_agreed": True,
    "scope_acknowledged": True,
}


def test_patient_goal_check_in_and_therapist_action_plan(tmp_path):
    client, factory = _setup(tmp_path)
    patient_headers = _headers("patient-1", "patient")
    therapist_headers = _headers("therapist-1", "therapist")
    try:
        goal = client.post("/api/v1/recovery-coaching/goals", headers=patient_headers, json=GOAL)
        assert goal.status_code == 201
        assert goal.json()["status"] == "proposed"

        urgent = client.post("/api/v1/recovery-coaching/check-ins", headers=patient_headers, json={
            "check_in_date": "2026-08-30", "energy": 2, "sleep_quality": 2,
            "stress": 4, "recovery_confidence": 2, "activity_minutes": 0,
            "barrier_category": "symptoms", "barrier_note": "New symptoms",
            "symptoms_changed": True, "urgent_concern": True,
            "scope_acknowledged": True,
        })
        assert urgent.status_code == 200
        assert urgent.json()["coaching_state"] == "urgent_escalation"
        assert "Coaching is paused" in urgent.json()["supportive_prompt"]

        dashboard = client.get("/api/v1/recovery-coaching/dashboard", headers=patient_headers)
        assert dashboard.status_code == 200
        assert dashboard.json()["summary"]["follow_up_needed"] == 1
        assert dashboard.json()["goals"][0]["goal_id"] == goal.json()["goal_id"]
        assert "psychotherapy" in dashboard.json()["scope"]["disclaimer"]

        action = client.post(
            "/api/v1/recovery-coaching/action-plans?patient_id=profile-1",
            headers=therapist_headers,
            json={
                "goal_id": goal.json()["goal_id"],
                "action_step": "Complete the agreed ten-minute walk after lunch",
                "frequency": "Three days per week",
                "support_needed": "Review symptom response at the next visit",
                "review_date": "2026-09-30",
                "patient_agreed": True,
            },
        )
        assert action.status_code == 201
        assert action.json()["status"] == "active"

        therapist_dashboard = client.get(
            "/api/v1/recovery-coaching/dashboard?patient_id=profile-1",
            headers=therapist_headers,
        )
        assert therapist_dashboard.status_code == 200
        assert therapist_dashboard.json()["action_plans"][0]["goal_id"] == goal.json()["goal_id"]

        with factory() as db:
            assert db.scalar(select(Notification).where(Notification.user_id == "therapist-1")) is not None
            actions = list(db.scalars(select(AuditLog.action).where(AuditLog.actor_user_id.in_(["patient-1", "therapist-1"]))).all())
            assert "recovery_coaching.goal_created" in actions
            assert "recovery_coaching.check_in_created" in actions
            assert "recovery_coaching.action_plan_created" in actions
    finally:
        app.dependency_overrides.clear()


def test_coaching_access_is_patient_and_assignment_scoped(tmp_path):
    client, _ = _setup(tmp_path)
    try:
        denied = client.get(
            "/api/v1/recovery-coaching/dashboard?patient_id=profile-2",
            headers=_headers("therapist-1", "therapist"),
        )
        assert denied.status_code == 403

        cross_patient = client.get(
            "/api/v1/recovery-coaching/dashboard?patient_id=profile-2",
            headers=_headers("patient-1", "patient"),
        )
        assert cross_patient.status_code == 403

        anonymous = client.get("/api/v1/recovery-coaching/dashboard")
        assert anonymous.status_code == 401

        future_check_in = client.post(
            "/api/v1/recovery-coaching/check-ins",
            headers=_headers("patient-1", "patient"),
            json={
                "check_in_date": (date.today() + timedelta(days=1)).isoformat(),
                "energy": 3, "sleep_quality": 3, "stress": 3,
                "recovery_confidence": 3, "activity_minutes": 0,
                "barrier_category": "none", "symptoms_changed": False,
                "urgent_concern": False, "scope_acknowledged": True,
            },
        )
        assert future_check_in.status_code == 422
    finally:
        app.dependency_overrides.clear()
