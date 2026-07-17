import sys
from pathlib import Path

from sqlalchemy.orm import sessionmaker

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "backend"))

from app.db.crud import create_patient_profile, delete_patient_profile, get_patient_profile, list_patient_profiles, update_patient_profile
from app.db.database import Base, create_database_engine
from app.schemas.patient_schema import PatientCreate, PatientUpdate


def db_for(tmp_path):
    engine = create_database_engine(f"sqlite:///{(tmp_path / 'patients.db').as_posix()}")
    Base.metadata.create_all(engine)
    return sessionmaker(bind=engine, expire_on_commit=False)()


def test_create_list_update_and_delete_development_profile(tmp_path):
    db = db_for(tmp_path)
    row = create_patient_profile(db, PatientCreate(display_name="Demo A", age_group="adult"))
    assert get_patient_profile(db, row.patient_id).display_name == "Demo A"
    assert len(list_patient_profiles(db)) == 1
    updated = update_patient_profile(db, row.patient_id, PatientUpdate(display_name="Demo B"))
    assert updated.display_name == "Demo B"
    assert delete_patient_profile(db, row.patient_id) is True
    assert get_patient_profile(db, row.patient_id) is None
