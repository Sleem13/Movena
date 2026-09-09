from datetime import datetime, timedelta, timezone

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from sqlalchemy.pool import StaticPool

from app.api.dependencies.auth import AuthError, require_super_admin
from app.db.models import (
    AuditLog,
    Base,
    DataRightsRequest,
    Notification,
    PatientProfile,
    User,
    UserConsent,
)
from app.services.admin_workflow_service import build_admin_workflow


@pytest.fixture
def workflow_db():
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
        full_name=f"Private {user_id}",
        role=role,
        is_active=True,
        is_verified=True,
    )


def test_workflow_snapshot_is_operational_and_deidentified(workflow_db: Session):
    now = datetime(2026, 8, 29, 9, 0, tzinfo=timezone.utc)
    root = _user("root-admin", "super_admin")
    patient_user = _user("patient-user", "patient")
    patient = PatientProfile(
        patient_id="patient-secret-12345678",
        user_id=patient_user.user_id,
        display_name="Never expose this patient name",
        notes="Never expose this clinical note",
        created_at=now - timedelta(days=2),
    )
    workflow_db.add_all([
        root,
        patient_user,
        patient,
        UserConsent(
            user_id=patient_user.user_id,
            consent_type="privacy",
            accepted=True,
            accepted_at=now - timedelta(days=2),
            version="2026-08",
        ),
        DataRightsRequest(
            request_id="privacy-request-87654321",
            user_id=patient_user.user_id,
            request_type="deletion",
            status="pending",
            details="Sensitive request details must not appear",
            created_at=now - timedelta(hours=80),
        ),
        AuditLog(
            actor_user_id=patient_user.user_id,
            action="data_rights.deletion_requested",
            resource_type="data_rights_request",
            resource_id="privacy-request-87654321",
            created_at=now - timedelta(hours=80),
        ),
        Notification(
            notification_id="recovery-alert-1",
            user_id=root.user_id,
            kind="password_reset_email_failed",
            title="Password reset email needs attention",
            body="Delivery failed for an account.",
            action_url="/admin/users/password-user-12345678",
            email_required=False,
            created_at=now - timedelta(minutes=5),
        ),
    ])
    workflow_db.commit()

    snapshot = build_admin_workflow(workflow_db, actor_user_id=root.user_id, now=now)

    assert snapshot["metrics"]["users"] == 2
    assert snapshot["metrics"]["patients"] == 1
    stages = {stage["key"]: stage for stage in snapshot["stages"]}
    assert stages["account_consent"]["attention_count"] == 1
    assert stages["therapist_assignment"]["attention_count"] == 1
    assert snapshot["privacy_requests"]["deletion"] == 1
    goals = {goal["key"]: goal for goal in snapshot["clinical_goals"]}
    assert goals["safety_boundaries"]["status"] == "attention"
    assert goals["safety_boundaries"]["attention_count"] == 2
    assert goals["function_first"]["status"] == "on_track"
    assert goals["therapist_review"]["attention_count"] >= 2
    assert snapshot["attention_queue"][0]["type"] == "privacy_request"
    assert snapshot["attention_queue"][0]["priority"] == "high"
    recovery = next(item for item in snapshot["attention_queue"] if item["type"] == "password_recovery")
    assert recovery["owner"] == "Account Support"
    assert recovery["action_url"] == "/admin/users/password-user-12345678"

    rendered = repr(snapshot)
    assert "Never expose this patient name" not in rendered
    assert "Never expose this clinical note" not in rendered
    assert "Sensitive request details must not appear" not in rendered
    assert "Private patient-user" not in rendered


def test_workflow_dependency_rejects_non_super_admin():
    with pytest.raises(AuthError) as error:
        require_super_admin(user=_user("ordinary-admin", "admin"))
    assert error.value.status_code == 403

    assert require_super_admin(user=_user("root-admin", "super_admin")).role == "super_admin"
