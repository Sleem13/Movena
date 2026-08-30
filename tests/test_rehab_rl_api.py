from fastapi.testclient import TestClient
from sqlalchemy.orm import sessionmaker

from app.core.security import create_access_token, get_password_hash
from app.db.database import Base, create_database_engine, get_db
from app.db.models import User
from app.main import app


SAFETY_SCREEN = {
    "red_flags_reviewed": True,
    "red_flags_present": False,
    "precautions_reviewed": True,
    "clinician_attestation": True,
}


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
                "safety_screen": SAFETY_SCREEN,
            },
        )
        assert assessment.status_code == 200
        assert assessment.json()["action_id"] in assessment.json()["valid_actions"]
        assert assessment.json()["prescription"]["exercises"]
        assert assessment.json()["decision_audit_id"]

        governance = client.get("/api/v1/rehab-rl/governance?days=30", headers=headers)
        assert governance.status_code == 200
        governance_payload = governance.json()
        assert governance_payload["scope"] == "clinician"
        assert governance_payload["decisions"] == 1
        assert governance_payload["safety_holds"] == 0
        assert governance_payload["modes"]["rehabrl_policy"] == 1
        assert governance_payload["policy_decisions"] == 1
        assert governance_payload["abstentions"] == 0
        assert governance_payload["abstention_rate"] == 0.0
        assert governance_payload["monitoring"]["automatic_promotion"] is False
        assert governance_payload["monitoring"]["clinical_approval_required"] is True
        assert governance_payload["audit"]["enabled"] is True
        assert governance_payload["recent"][0]["decision_id"] == assessment.json()["decision_audit_id"]

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
        assert len(library.json()["conditions"]) == 26
        assert sum(item["rl_supported"] for item in library.json()["conditions"]) == 12

        protocols = client.get("/api/v1/rehab-rl/protocols", headers=headers)
        assert protocols.status_code == 200
        assert len(protocols.json()["items"]) == 26
        acl = next(item for item in protocols.json()["items"] if item["id"] == "acl_tear")
        assert len(acl["phases"]) == 5
        assert acl["red_flags"]
        assert acl["outcome_measures"]
    finally:
        app.dependency_overrides.clear()


def test_non_rl_condition_returns_protocol_without_model_prediction(tmp_path):
    client = _client_for_roles(tmp_path, "therapist")
    try:
        response = client.post(
            "/api/v1/rehab-rl/assessment",
            headers=_headers("therapist"),
            json={"condition_id": "stroke_rehabilitation", "recovery_stage": 2, "safety_screen": SAFETY_SCREEN},
        )
        assert response.status_code == 200
        payload = response.json()
        assert payload["mode"] == "protocol_reference"
        assert payload["action_id"] is None
        assert payload["confidence"] is None
        assert payload["load_caution"] in {"Low", "Moderate", "High"}
        assert payload["clinical_safety"]["red_flags_screened"] is True
        assert payload["q_values"] == []
        assert payload["protocol"]["rl_supported"] is False
        assert payload["phase_plan"]["stage"] == 2
        assert payload["phase_plan"]["progression_criteria"]
    finally:
        app.dependency_overrides.clear()


def test_safety_gate_withholds_policy_and_refers_when_red_flag_present(tmp_path):
    client = _client_for_roles(tmp_path, "therapist")
    try:
        response = client.post(
            "/api/v1/rehab-rl/assessment",
            headers=_headers("therapist"),
            json={
                "condition_id": "acl_tear",
                "safety_screen": {**SAFETY_SCREEN, "red_flags_present": True},
            },
        )
        assert response.status_code == 200
        payload = response.json()
        assert payload["mode"] == "safety_hold"
        assert payload["clinical_safety"]["treatment_readiness"] == "hold_and_refer"
        assert payload["action_id"] is None
        assert payload["q_values"] == []
        assert payload["prescription"]["exercises"] == []

        governance = client.get("/api/v1/rehab-rl/governance", headers=_headers("therapist"))
        assert governance.status_code == 200
        assert governance.json()["safety_holds"] == 1
        assert governance.json()["referrals"] == 1
        assert governance.json()["abstentions"] == 1
        assert governance.json()["abstention_rate"] == 1.0
    finally:
        app.dependency_overrides.clear()


def test_postoperative_case_requires_procedure_orders_and_manifest_is_compatible(tmp_path):
    client = _client_for_roles(tmp_path, "therapist")
    headers = _headers("therapist")
    try:
        held = client.post(
            "/api/v1/rehab-rl/assessment",
            headers=headers,
            json={
                "condition_id": "rotator_cuff_tear",
                "safety_screen": {**SAFETY_SCREEN, "postoperative": True},
            },
        )
        assert held.status_code == 200
        assert held.json()["clinical_safety"]["treatment_readiness"] == "procedure_orders_required"

        manifest = client.get("/api/v1/rehab-rl/model-manifest", headers=headers)
        assert manifest.status_code == 200
        assert manifest.json()["checkpoint"]["compatible"] is True
        assert manifest.json()["contract"]["state_dim"] == 32
        assert manifest.json()["contract"]["action_dim"] == 30
        assert len(manifest.json()["contract"]["injury_labels"]) == 12
        assert len(manifest.json()["contract"]["sha256"]) == 64
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
