from datetime import datetime, timedelta, timezone

from fastapi.testclient import TestClient
from sqlalchemy import select
from sqlalchemy.orm import sessionmaker

from app.api.v1 import auth as auth_routes
from app.core.authorization import permissions_for_role
from app.core.config import get_settings
from app.core.security import create_access_token, get_password_hash
from app.services.auth_token_service import token_hash
from app.db.database import Base, create_database_engine, get_db, init_db
from app.db.models import User
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
            "email": "new@example.com", "password": "StrongPassword123", "full_name": "New User", "role": "patient"
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
            "email": "new@example.com", "password": "DifferentPassword123", "role": "researcher_demo"
        })
        assert duplicate.status_code == 409
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
