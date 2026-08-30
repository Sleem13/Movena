from datetime import datetime, timedelta, timezone

from fastapi.testclient import TestClient
from sqlalchemy import inspect, select, text
from sqlalchemy.orm import sessionmaker

from app.api.v1 import auth as auth_routes
from app.core.authorization import permissions_for_role
from app.core.config import get_settings
from app.core.security import create_access_token, get_password_hash
from app.services.auth_token_service import token_hash
from app.db.database import Base, create_database_engine, get_db, init_db
from app.db.models import Notification, User
from app.main import app


def auth_client(tmp_path):
    engine = create_database_engine(f"sqlite:///{(tmp_path / 'verification.db').as_posix()}")
    Base.metadata.create_all(engine)
    factory = sessionmaker(bind=engine, expire_on_commit=False)

    def override():
        db = factory()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override
    return TestClient(app), factory


def test_registration_persists_role_permissions_and_requires_verification(tmp_path, monkeypatch):
    monkeypatch.setenv("REQUIRE_EMAIL_VERIFICATION", "true")
    get_settings.cache_clear()
    client, factory = auth_client(tmp_path)
    messages = []
    monkeypatch.setattr(auth_routes, "send_verification_email", lambda email, token: messages.append((email, token)))
    try:
        created = client.post("/api/v1/auth/register", json={
            "username": "new.user", "email": "new@example.com", "password": "StrongPassword123", "full_name": "New User", "role": "patient"
        })
        assert created.status_code == 201
        assert created.json()["role"] == "patient"
        assert created.json()["permissions"] == permissions_for_role("patient")
        assert created.json()["is_verified"] is False

        denied = client.post("/api/v1/auth/login", json={"email": "new@example.com", "password": "StrongPassword123"})
        assert denied.status_code == 403 and denied.json()["error_code"] == "EMAIL_NOT_VERIFIED"

        token = messages[0][1]
        db = factory()
        stored = db.scalar(select(User).where(User.email == "new@example.com"))
        assert stored.role == "patient" and stored.permissions == permissions_for_role("patient")
        assert stored.verification_token_hash != token
        db.close()

        verified = client.post("/api/v1/auth/verify-email", json={"token": token})
        assert verified.status_code == 200
        assert client.post("/api/v1/auth/verify-email", json={"token": token}).status_code == 400
        assert client.post("/api/v1/auth/login", json={"email": "new@example.com", "password": "StrongPassword123"}).status_code == 200

        duplicate = client.post("/api/v1/auth/register", json={
            "username": "different.user", "email": "new@example.com", "password": "DifferentPassword123", "full_name": "Different User", "role": "researcher_demo"
        })
        assert duplicate.status_code == 409
        duplicate_username = client.post("/api/v1/auth/register", json={
            "username": "NEW.USER", "email": "other@example.com", "password": "DifferentPassword123", "full_name": "Other User", "role": "researcher_demo"
        })
        assert duplicate_username.status_code == 409
        db = factory(); retained = db.scalar(select(User).where(User.email == "new@example.com")); db.close()
        assert retained.role == "patient" and retained.permissions == permissions_for_role("patient")
    finally:
        app.dependency_overrides.clear()
        get_settings.cache_clear()


def test_resend_and_single_use_password_recovery(tmp_path, monkeypatch):
    client, factory = auth_client(tmp_path)
    verification_tokens = []
    reset_tokens = []
    monkeypatch.setattr(auth_routes, "send_verification_email", lambda email, token: verification_tokens.append(token))
    monkeypatch.setattr(auth_routes, "send_password_reset_email", lambda email, token: reset_tokens.append(token))
    try:
        db = factory()
        db.add(User(
            user_id="verified-1", email="verified@example.com", password_hash=get_password_hash("StrongPassword123"),
            role="researcher_demo", permissions_json='["analysis:create"]', is_verified=True,
        ))
        db.commit(); db.close()

        generic = client.post("/api/v1/auth/forgot-password", json={"email": "missing@example.com"})
        requested = client.post("/api/v1/auth/forgot-password", json={"email": "verified@example.com"})
        assert generic.status_code == requested.status_code == 200
        assert generic.json()["message"] == requested.json()["message"]
        assert len(reset_tokens) == 1

        old_session = create_access_token("verified-1", "researcher_demo")
        reset = client.post("/api/v1/auth/reset-password", json={
            "token": reset_tokens[0], "new_password": "ReplacementPassword123"
        })
        assert reset.status_code == 200
        assert client.post("/api/v1/auth/reset-password", json={
            "token": reset_tokens[0], "new_password": "AnotherPassword123"
        }).status_code == 400
        revoked = client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {old_session}"})
        assert revoked.status_code == 401 and revoked.json()["error_code"] == "TOKEN_REVOKED"
        assert client.post("/api/v1/auth/login", json={
            "email": "verified@example.com", "password": "ReplacementPassword123"
        }).status_code == 200

        db = factory(); user = db.scalar(select(User).where(User.user_id == "verified-1")); user.reset_password_token_hash = token_hash("x" * 32); user.reset_password_expires = datetime.now(timezone.utc) - timedelta(seconds=1); db.commit(); db.close()
        expired = client.post("/api/v1/auth/reset-password", json={
            "token": "x" * 32, "new_password": "AnotherPassword123"
        })
        assert expired.status_code == 400
    finally:
        app.dependency_overrides.clear()


def test_password_recovery_email_failure_notifies_super_admin_without_exposing_token(tmp_path, monkeypatch):
    client, factory = auth_client(tmp_path)

    def fail_delivery(email, token):
        raise auth_routes.EmailDeliveryError("SMTP unavailable")

    monkeypatch.setattr(auth_routes, "send_password_reset_email", fail_delivery)
    try:
        db = factory()
        db.add_all([
            User(
                user_id="root-admin", username="root-admin", email="root@example.com",
                password_hash=get_password_hash("StrongPassword123"), role="super_admin",
                is_verified=True, is_active=True, account_status="active",
            ),
            User(
                user_id="recovery-user", username="recovery-user", email="recover@example.com",
                password_hash=get_password_hash("StrongPassword123"), role="patient",
                is_verified=True, is_active=True, account_status="active",
            ),
        ])
        db.commit()
        db.close()

        response = client.post("/api/v1/auth/forgot-password", json={"email": "recover@example.com"})
        missing = client.post("/api/v1/auth/forgot-password", json={"email": "missing@example.com"})
        assert response.status_code == missing.status_code == 200
        assert response.json()["message"] == missing.json()["message"]

        db = factory()
        user = db.scalar(select(User).where(User.user_id == "recovery-user"))
        alerts = db.scalars(select(Notification).where(
            Notification.user_id == "root-admin",
            Notification.kind == "password_reset_email_failed",
        )).all()
        assert user.reset_password_token_hash is None
        assert user.reset_password_expires is None
        assert user.reset_password_sent_at is not None
        assert len(alerts) == 1
        assert alerts[0].action_url == "/admin/users/recovery-user"
        assert "recover@example.com" in alerts[0].body
        assert "token" not in alerts[0].body.lower()
        assert alerts[0].email_required is False
        db.close()

        repeated = client.post("/api/v1/auth/forgot-password", json={"email": "recover@example.com"})
        assert repeated.status_code == 200
        db = factory()
        assert len(db.scalars(select(Notification).where(
            Notification.user_id == "root-admin",
            Notification.kind == "password_reset_email_failed",
        )).all()) == 1
        db.close()
    finally:
        app.dependency_overrides.clear()


def test_unverified_legacy_user_has_full_access_when_verification_is_disabled(tmp_path, monkeypatch):
    monkeypatch.setenv("REQUIRE_EMAIL_VERIFICATION", "false")
    get_settings.cache_clear()
    client, factory = auth_client(tmp_path)
    reset_tokens = []
    monkeypatch.setattr(auth_routes, "send_password_reset_email", lambda email, token: reset_tokens.append(token))
    try:
        db = factory()
        db.add(User(
            user_id="legacy-unverified", email="legacy@example.com",
            password_hash=get_password_hash("StrongPassword123"), role="therapist",
            permissions_json='["analysis:create"]', is_verified=False,
        ))
        db.commit(); db.close()

        login = client.post("/api/v1/auth/login", json={
            "email": "legacy@example.com", "password": "StrongPassword123",
        })
        assert login.status_code == 200
        headers = {"Authorization": f"Bearer {login.json()['access_token']}"}
        current_user = client.get("/api/v1/auth/me", headers=headers)
        assert current_user.status_code == 200
        assert current_user.json()["email"] == "legacy@example.com"

        recovery = client.post("/api/v1/auth/forgot-password", json={"email": "legacy@example.com"})
        assert recovery.status_code == 200
        assert len(reset_tokens) == 1
    finally:
        app.dependency_overrides.clear()
        get_settings.cache_clear()


def test_compatibility_migration_never_overwrites_existing_role(tmp_path):
    engine = create_database_engine(f"sqlite:///{(tmp_path / 'roles-retained.db').as_posix()}")
    Base.metadata.create_all(engine)
    factory = sessionmaker(bind=engine, expire_on_commit=False)
    db = factory()
    db.add(User(
        user_id="role-1", email="role@example.com", password_hash="not-used",
        role="therapist", permissions_json="[]", is_verified=True,
    ))
    db.commit(); db.close()
    init_db(engine)
    init_db(engine)
    db = factory(); user = db.scalar(select(User).where(User.user_id == "role-1")); db.close()
    assert user.role == "therapist"
    assert user.permissions == permissions_for_role("therapist")
    assert user.username == "role"


def test_compatibility_migration_assigns_unique_legacy_usernames(tmp_path):
    engine = create_database_engine(f"sqlite:///{(tmp_path / 'legacy-usernames.db').as_posix()}")
    Base.metadata.create_all(engine)
    factory = sessionmaker(bind=engine, expire_on_commit=False)
    db = factory()
    db.add_all([
        User(user_id="existing", username="person", email="existing@example.com", password_hash="not-used", role="patient"),
        User(user_id="legacy", email="person@example.com", password_hash="not-used", role="patient"),
    ])
    db.commit(); db.close()

    init_db(engine)

    db = factory(); legacy = db.scalar(select(User).where(User.user_id == "legacy")); db.close()
    assert legacy.username == "person-2"


def test_compatibility_migration_adds_rehabilitation_phase_columns(tmp_path):
    database_path = tmp_path / "legacy-rehabilitation.db"
    engine = create_database_engine(f"sqlite:///{database_path.as_posix()}")
    with engine.begin() as connection:
        connection.execute(text("CREATE TABLE analysis_sessions (id INTEGER PRIMARY KEY)"))
        connection.execute(text("CREATE TABLE exercise_plan_items (id INTEGER PRIMARY KEY)"))
        connection.execute(text("CREATE TABLE adherence_entries (id INTEGER PRIMARY KEY)"))

    init_db(engine)
    init_db(engine)

    inspector = inspect(engine)
    assert {"plan_item_id"} <= {
        column["name"] for column in inspector.get_columns("analysis_sessions")
    }
    assert {
        "rest_interval_seconds", "tempo", "target_rom_degrees", "target_score",
        "requires_ai_analysis", "status",
    } <= {column["name"] for column in inspector.get_columns("exercise_plan_items")}
    assert {"fatigue", "analysis_session_id"} <= {
        column["name"] for column in inspector.get_columns("adherence_entries")
    }


def test_compatibility_migration_adds_recovery_review_columns(tmp_path):
    engine = create_database_engine(
        f"sqlite:///{(tmp_path / 'legacy-coaching.db').as_posix()}"
    )
    with engine.begin() as connection:
        connection.execute(
            text("CREATE TABLE recovery_coaching_check_ins (id INTEGER PRIMARY KEY)")
        )

    init_db(engine)
    init_db(engine)

    columns = {
        column["name"]
        for column in inspect(engine).get_columns("recovery_coaching_check_ins")
    }
    assert {
        "reviewed_at",
        "reviewed_by_user_id",
        "review_disposition",
        "review_note",
    } <= columns
