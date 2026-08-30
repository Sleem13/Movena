from fastapi.testclient import TestClient
from sqlalchemy.orm import sessionmaker

from app.core.security import create_access_token, get_password_hash
from app.db.database import Base, create_database_engine, get_db
from app.db.models import User
from app.main import app


def _client_for_roles(tmp_path, *roles):
    engine = create_database_engine(f"sqlite:///{(tmp_path / 'rehab-rl.db').as_posix()}")
    Base.metadata.create_all(engine)
    factory = sessionmaker(bind=engine, expire_on_commit=False)
    with factory() as db:
        for role in roles:
            db.add(
                User(
                    user_id=f"{role}-1",
                    email=f"{role}@example.com",
                    password_hash=get_password_hash("StrongPassword123"),
                    role=role,
                    is_verified=True,
                )
            )
        db.commit()

    def override():
        session = factory()
        try:
            yield session
        finally:
            session.close()

    app.dependency_overrides[get_db] = override
    return TestClient(app)


def _headers(role):
    return {"Authorization": f"Bearer {create_access_token(f'{role}-1', role)}"}


def test_rehab_rl_requires_clinical_role(tmp_path):
    client = _client_for_roles(tmp_path, "patient")
    try:
        response = client.get("/api/v1/rehab-rl/overview", headers=_headers("patient"))
        assert response.status_code == 403
        assert response.json()["error_code"] == "INSUFFICIENT_ROLE"
    finally:
        app.dependency_overrides.clear()


def test_therapist_can_assess_simulate_and_read_library(tmp_path):
    client = _client_for_roles(tmp_path, "therapist")
    headers = _headers("therapist")
    try:
        overview = client.get("/api/v1/rehab-rl/overview", headers=headers)
        assert overview.status_code == 200
        assert overview.json()["metrics"]["state_features"] == 32

        assessment = client.post(
            "/api/v1/rehab-rl/assessment",
            headers=headers,
            json={
                "injury_type": "ACL Tear",
                "recovery_stage": 1,
                "pain_level": 0.5,
                "rom": 0.6,
                "strength": 0.55,
            },
        )
        assert assessment.status_code == 200
        assert assessment.json()["action_id"] in assessment.json()["valid_actions"]
        assert assessment.json()["prescription"]["exercises"]

        simulation = client.post(
            "/api/v1/rehab-rl/simulate",
            headers=headers,
            json={"injury_type": "Ankle Sprain", "sessions": 5},
        )
        assert simulation.status_code == 200
        assert 0 < simulation.json()["sessions"] <= 5

        library = client.get("/api/v1/rehab-rl/exercises", headers=headers)
        assert library.status_code == 200
        assert len(library.json()["items"]) > 40
    finally:
        app.dependency_overrides.clear()


def test_model_operations_are_super_admin_only(tmp_path):
    client = _client_for_roles(tmp_path, "therapist", "super_admin")
    try:
        denied = client.get(
            "/api/v1/rehab-rl/inspector", headers=_headers("therapist")
        )
        assert denied.status_code == 403

        inspector = client.get(
            "/api/v1/rehab-rl/inspector", headers=_headers("super_admin")
        )
        assert inspector.status_code == 200
        assert len(inspector.json()["architecture"]) == 4

        restored = client.post(
            "/api/v1/rehab-rl/checkpoints/restore",
            headers=_headers("super_admin"),
        )
        assert restored.status_code == 200
        assert restored.json()["message"] == "Checkpoint restored"
    finally:
        app.dependency_overrides.clear()
