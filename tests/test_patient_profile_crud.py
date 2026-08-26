import sys
from pathlib import Path

from sqlalchemy.orm import sessionmaker

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "backend"))

from app.db.crud import (
    create_exercise_plan, create_patient_profile, delete_patient_profile, get_patient_profile,
    list_exercise_plans, list_patient_profiles, update_exercise_plan_status, update_patient_profile,
)
from app.db.database import Base, create_database_engine
from app.schemas.patient_schema import ExercisePlanCreate, ExercisePlanItemCreate, PatientCreate, PatientUpdate


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


def test_create_and_update_patient_exercise_plan(tmp_path):
    db = db_for(tmp_path)
    patient = create_patient_profile(db, PatientCreate(display_name="Patient 1042"))
    plan = create_exercise_plan(db, patient.patient_id, ExercisePlanCreate(
        title="Lower-limb home plan",
        notes="Clinician-authored plan.",
        items=[
            ExercisePlanItemCreate(
                exercise_id="bodyweight_squat", sets=3, reps=8, days_per_week=3,
                instructions="Use a stable support if needed.",
            ),
            ExercisePlanItemCreate(
                exercise_id="sit_to_stand", sets=2, reps=6, days_per_week=4,
            ),
        ],
    ), "therapist-user")

    assert plan.status == "active"
    assert [item.exercise_id for item in plan.items] == ["bodyweight_squat", "sit_to_stand"]
    assert list_exercise_plans(db, patient.patient_id)[0].created_by_user_id == "therapist-user"
    updated = update_exercise_plan_status(db, patient.patient_id, plan.plan_id, "completed")
    assert updated is not None and updated.status == "completed"
