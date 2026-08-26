from fastapi.testclient import TestClient
from sqlalchemy import select
from sqlalchemy.orm import sessionmaker

from app.core.security import create_access_token, get_password_hash
from app.db.database import Base, create_database_engine, get_db
from app.db.models import AuditLog, User
from app.main import app
from app.services.admin_seed_service import seed_admin, seed_super_admin
import pytest


def test_super_admin_seed_requires_eight_character_password(tmp_path):
    engine = create_database_engine(f"sqlite:///{(tmp_path / 'short-password.db').as_posix()}")
    factory = sessionmaker(bind=engine, expire_on_commit=False)
    Base.metadata.create_all(engine)
    db = factory()

    with pytest.raises(ValueError, match="at least 8 characters"):
        seed_super_admin("owner@example.com", "short7", "Owner", db=db)

    db.close()


def test_super_admin_manages_accounts_and_protected_account_is_immutable(tmp_path):
    engine = create_database_engine(f"sqlite:///{(tmp_path / 'super-admin.db').as_posix()}")
    Base.metadata.create_all(engine)
    factory = sessionmaker(bind=engine, expire_on_commit=False)
    db = factory()
    root, _ = seed_super_admin("owner@example.com", "StrongPassword123", "Owner", db=db)
    admin = User(
        user_id="admin-1",
        email="admin@example.com",
        password_hash=get_password_hash("StrongPassword123"),
        role="admin",
        is_verified=True,
    )
    patient = User(
        user_id="patient-1",
        email="patient@example.com",
        password_hash=get_password_hash("StrongPassword123"),
        role="patient",
    )
    db.add_all([admin, patient])
    db.commit()
    root_id = root.user_id
    db.close()

    def override():
        session = factory()
        try:
            yield session
        finally:
            session.close()

    app.dependency_overrides[get_db] = override
    client = TestClient(app)
    root_headers = {"Authorization": f"Bearer {create_access_token(root_id, 'super_admin')}"}
    admin_headers = {"Authorization": f"Bearer {create_access_token('admin-1', 'admin')}"}
    try:
        assert client.get("/api/v1/admin/users", headers=admin_headers).status_code == 403
        listing = client.get("/api/v1/admin/users", headers=root_headers)
        assert listing.status_code == 200
        assert {row["email"] for row in listing.json()} == {
            "owner@example.com", "admin@example.com", "patient@example.com"
        }

        created = client.post(
            "/api/v1/admin/users",
            headers=root_headers,
            json={
                "username": "therapist.one",
                "email": "therapist@example.com",
                "full_name": "Therapist One",
                "password": "AssignedPassword123",
                "role": "therapist",
            },
        )
        assert created.status_code == 201
        assert created.json()["username"] == "therapist.one"
        assert created.json()["role"] == "therapist"
        assert created.json()["is_verified"] is True
        logged = client.post(
            "/api/v1/auth/login",
            json={"email": "therapist.one", "password": "AssignedPassword123"},
        )
        assert logged.status_code == 200
        assert logged.json()["user"]["email"] == "therapist@example.com"

        duplicate = client.post(
            "/api/v1/admin/users",
            headers=root_headers,
            json={
                "username": "therapist.one",
                "email": "another@example.com",
                "full_name": "Another Therapist",
                "password": "AssignedPassword123",
                "role": "therapist",
            },
        )
        assert duplicate.status_code == 409

        paused = client.patch(
            "/api/v1/admin/users/patient-1/status",
            headers=root_headers,
            json={"status": "paused", "reason": "Requested by account owner"},
        )
        assert paused.status_code == 200
        assert client.post(
            "/api/v1/auth/login",
            json={"email": "patient@example.com", "password": "StrongPassword123"},
        ).json()["error_code"] == "ACCOUNT_PAUSED"

        protected = client.delete(
            f"/api/v1/admin/users/{root_id}",
            headers=root_headers,
            params={"reason": "Should never work"},
        )
        assert protected.status_code == 403
        assert protected.json()["error_code"] == "PROTECTED_ACCOUNT"

        changed = client.post(
            "/api/v1/admin/users/admin-1/password",
            headers=root_headers,
            json={"new_password": "AnotherStrongPassword123", "reason": "Security rotation"},
        )
        assert changed.status_code == 200
        revoked = client.get("/api/v1/auth/me", headers=admin_headers)
        assert revoked.status_code == 401
        assert revoked.json()["error_code"] == "TOKEN_REVOKED"

        session = factory()
        actions = set(session.scalars(select(AuditLog.action)).all())
        session.close()
        assert {"user.created", "user.status_changed", "user.password_reset"}.issubset(actions)
    finally:
        app.dependency_overrides.clear()


def test_super_admin_seed_is_protected_and_idempotent(tmp_path):
    engine = create_database_engine(f"sqlite:///{(tmp_path / 'super-seed.db').as_posix()}")
    Base.metadata.create_all(engine)
    db = sessionmaker(bind=engine, expire_on_commit=False)()
    first, changed = seed_super_admin("owner@example.com", "StrongPassword123", "Owner", db=db)
    second, changed_again = seed_super_admin("owner@example.com", "StrongPassword123", "Owner", db=db)
    assert changed and not changed_again
    assert first.user_id == second.user_id
    assert first.role == "super_admin" and first.is_protected and first.is_active
    with pytest.raises(ValueError, match="protected"):
        seed_admin("owner@example.com", "StrongPassword123", "Admin", reset=True, db=db)
    db.refresh(first)
    assert first.role == "super_admin" and first.is_protected
    db.close()
