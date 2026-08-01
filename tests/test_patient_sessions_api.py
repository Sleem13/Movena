import sys
from pathlib import Path

from fastapi.testclient import TestClient
from sqlalchemy.orm import sessionmaker

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "backend"))

from app.db.crud import create_patient_profile
from app.db.database import Base, create_database_engine, get_db
from app.main import app
from app.schemas.analysis_schema import AnalysisResponse
from app.schemas.patient_schema import PatientCreate
from app.services.session_persistence_service import save_analysis_session
from app.api.dependencies.auth import get_current_user
from types import SimpleNamespace


def test_assign_list_and_progress_api_with_clean_invalid_ids(tmp_path):
    engine = create_database_engine(f"sqlite:///{(tmp_path / 'patient_sessions.db').as_posix()}")
    Base.metadata.create_all(engine); factory = sessionmaker(bind=engine, expire_on_commit=False)
    seed = factory(); patient = create_patient_profile(seed, PatientCreate(display_name="Demo")); saved = save_analysis_session(AnalysisResponse(total_reps=3), db=seed)
    def override():
        db = factory()
        try: yield db
        finally: db.close()
    app.dependency_overrides[get_db] = override
    app.dependency_overrides[get_current_user] = lambda: SimpleNamespace(user_id="therapist", role="therapist")
    try:
        client = TestClient(app)
        assigned = client.post(f"/api/v1/therapist/patients/{patient.patient_id}/sessions/{saved.session_id}")
        assert assigned.status_code == 200
        sessions = client.get(f"/api/v1/therapist/patients/{patient.patient_id}/sessions")
        assert sessions.status_code == 200 and len(sessions.json()) == 1
        progress = client.get(f"/api/v1/therapist/patients/{patient.patient_id}/progress")
        assert progress.json()["total_sessions"] == 1
        assert "metric_provenance" in progress.json()
        assert client.post(f"/api/v1/therapist/patients/{patient.patient_id}/sessions/missing").status_code == 404
        assert client.get("/api/v1/therapist/patients/missing/sessions").status_code == 404
    finally:
        app.dependency_overrides.clear(); seed.close()
