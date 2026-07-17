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
        assert "prototype" in empty.json()["prototype_warning"].lower()
        created = client.post("/api/v1/therapist/patients", json={"display_name": "Development Profile", "age_group": "adult"})
        assert created.status_code == 201
        patient_id = created.json()["patient_id"]
        assert client.get("/api/v1/therapist/patients").json()[0]["display_name"] == "Development Profile"
        patched = client.patch(f"/api/v1/therapist/patients/{patient_id}", json={"clinical_group": "unknown"})
        assert patched.status_code == 200 and patched.json()["clinical_group"] == "unknown"
        assert client.get("/api/v1/therapist/patients/missing").status_code == 404
        assert client.delete(f"/api/v1/therapist/patients/{patient_id}").status_code == 200
    finally: app.dependency_overrides.clear()
