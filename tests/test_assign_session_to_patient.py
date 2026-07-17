import sys
from pathlib import Path

from sqlalchemy.orm import sessionmaker

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "backend"))

from app.db.crud import assign_session_to_patient, create_patient_profile, delete_patient_profile
from app.db.database import Base, create_database_engine
from app.schemas.analysis_schema import AnalysisResponse
from app.schemas.patient_schema import PatientCreate
from app.services.session_persistence_service import save_analysis_session


def test_assign_and_unassign_session_when_profile_deleted(tmp_path):
    engine = create_database_engine(f"sqlite:///{(tmp_path / 'assign.db').as_posix()}")
    Base.metadata.create_all(engine)
    db = sessionmaker(bind=engine, expire_on_commit=False)()
    patient = create_patient_profile(db, PatientCreate(display_name="Demo Profile"))
    session = save_analysis_session(AnalysisResponse(total_reps=2), db=db)
    assigned = assign_session_to_patient(db, patient.patient_id, session.session_id)
    assert assigned.patient_id == patient.patient_id
    assert delete_patient_profile(db, patient.patient_id)
    db.refresh(assigned)
    assert assigned.patient_id is None


def test_save_with_invalid_patient_is_safely_unassigned(tmp_path):
    engine = create_database_engine(f"sqlite:///{(tmp_path / 'invalid.db').as_posix()}")
    Base.metadata.create_all(engine)
    db = sessionmaker(bind=engine, expire_on_commit=False)()
    saved = save_analysis_session(AnalysisResponse(total_reps=1), db=db, patient_id="missing")
    assert saved.patient_id is None
    assert saved.patient_assignment_warning is True
