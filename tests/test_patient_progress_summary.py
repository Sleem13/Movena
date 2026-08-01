import sys
from pathlib import Path

from sqlalchemy.orm import sessionmaker

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "backend"))

from app.db.crud import create_patient_profile, get_patient_progress_summary
from app.db.database import Base, create_database_engine
from app.schemas.analysis_schema import AnalysisConfidence, AnalysisResponse
from app.schemas.patient_schema import PatientCreate
from app.services.session_persistence_service import save_analysis_session


def test_progress_handles_empty_and_multiple_exercises(tmp_path):
    engine = create_database_engine(f"sqlite:///{(tmp_path / 'progress.db').as_posix()}")
    Base.metadata.create_all(engine)
    db = sessionmaker(bind=engine, expire_on_commit=False)()
    patient = create_patient_profile(db, PatientCreate(display_name="Demo"))
    empty = get_patient_progress_summary(db, patient.patient_id)
    assert empty.total_sessions == 0 and empty.average_movement_score is None
    save_analysis_session(AnalysisResponse(
        exercise="bodyweight_squat", movement_score=80,
        analysis_confidence=AnalysisConfidence(score=0.4, level="low"),
        detected_issues=["poor_depth"],
    ), db=db, patient_id=patient.patient_id)
    save_analysis_session(AnalysisResponse(
        exercise="sit_to_stand", movement_score=90,
        analysis_confidence=AnalysisConfidence(score=0.8, level="high"),
        detected_issues=["poor_control"],
    ), db=db, patient_id=patient.patient_id)
    progress = get_patient_progress_summary(db, patient.patient_id)
    assert progress.total_sessions == 2
    assert progress.sessions_by_exercise == {"bodyweight_squat": 1, "sit_to_stand": 1}
    assert progress.average_movement_score == 85
    assert progress.movement_score_observation_count == 2
    assert progress.analysis_confidence_observation_count == 2
    assert progress.low_confidence_session_count == 1
    assert any("movement_score" in item for item in progress.metric_provenance)
    assert {item.issue_code for item in progress.detected_issue_counts} == {"poor_depth", "poor_control"}
