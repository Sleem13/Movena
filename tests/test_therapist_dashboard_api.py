import sys
from pathlib import Path

from fastapi.testclient import TestClient
from sqlalchemy.orm import sessionmaker

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "backend"))

from app.db.database import Base, create_database_engine, get_db
from app.main import app
from app.api.dependencies.auth import get_current_user
from types import SimpleNamespace


def test_dashboard_and_patient_crud_api(tmp_path):
    engine = create_database_engine(f"sqlite:///{(tmp_path / 'therapist.db').as_posix()}")
    Base.metadata.create_all(engine); factory = sessionmaker(bind=engine, expire_on_commit=False)
    from app.db.models import User
    with factory() as seed:
        seed.add(User(user_id="therapist", email="therapist@example.com", password_hash="test", role="therapist", is_active=True, account_status="active"))
        seed.commit()
    def override():
        db = factory()
        try: yield db
        finally: db.close()
    app.dependency_overrides[get_db] = override
    app.dependency_overrides[get_current_user] = lambda: SimpleNamespace(user_id="therapist", role="therapist")
    try:
        client = TestClient(app)
        empty = client.get("/api/v1/therapist/dashboard")
        assert empty.status_code == 200 and empty.json()["total_patients"] == 0
        assert "privacy notice" in empty.json()["prototype_warning"].lower()
        created = client.post("/api/v1/therapist/patients", json={"display_name": "Patient 1042", "age_group": "adult"})
        assert created.status_code == 201
        patient_id = created.json()["patient_id"]
        assert client.get("/api/v1/therapist/patients").json()[0]["display_name"] == "Patient 1042"
        patched = client.patch(f"/api/v1/therapist/patients/{patient_id}", json={"clinical_group": "unknown"})
        assert patched.status_code == 200 and patched.json()["clinical_group"] == "unknown"
        plan = client.post(f"/api/v1/therapist/patients/{patient_id}/exercise-plans", json={
            "title": "Home exercise plan",
            "notes": "Reviewed with the patient.",
            "items": [{
                "exercise_id": "bodyweight_squat", "sets": 3, "reps": 8,
                "days_per_week": 3, "instructions": "Use support if needed.",
            }],
        })
        assert plan.status_code == 201
        assert plan.json()["created_by_user_id"] == "therapist"
        assert plan.json()["items"][0]["sets"] == 3
        plans = client.get(f"/api/v1/therapist/patients/{patient_id}/exercise-plans")
        assert plans.status_code == 200 and len(plans.json()) == 1
        completed = client.patch(
            f"/api/v1/therapist/patients/{patient_id}/exercise-plans/{plan.json()['plan_id']}",
            json={"status": "completed"},
        )
        assert completed.status_code == 200 and completed.json()["status"] == "completed"
        assert client.get("/api/v1/therapist/patients/missing").status_code == 404
        assert client.delete(f"/api/v1/therapist/patients/{patient_id}").status_code == 200
    finally: app.dependency_overrides.clear()
