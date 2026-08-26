import sys
from datetime import datetime, timedelta, timezone
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
    squat_baseline = save_analysis_session(AnalysisResponse(
        exercise="bodyweight_squat", movement_score=80,
        total_reps=5,
        analysis_confidence=AnalysisConfidence(score=0.4, level="low"),
        detected_issues=["poor_depth"],
    ), db=db, patient_id=patient.patient_id)
    squat_baseline.created_at = datetime.now(timezone.utc) - timedelta(days=7)
    db.commit()
    save_analysis_session(AnalysisResponse(
        exercise="bodyweight_squat", movement_score=88, total_reps=7,
        analysis_confidence=AnalysisConfidence(score=0.9, level="high"),
    ), db=db, patient_id=patient.patient_id)
    save_analysis_session(AnalysisResponse(
        exercise="sit_to_stand", movement_score=90,
        analysis_confidence=AnalysisConfidence(score=0.8, level="high"),
        detected_issues=["poor_control"],
    ), db=db, patient_id=patient.patient_id)
    progress = get_patient_progress_summary(db, patient.patient_id)
    assert progress.total_sessions == 3
    assert progress.sessions_by_exercise == {"bodyweight_squat": 2, "sit_to_stand": 1}
    assert progress.average_movement_score == 86
    assert progress.movement_score_observation_count == 3
    assert progress.analysis_confidence_observation_count == 3
    assert progress.low_confidence_session_count == 1
    assert any("movement_score" in item for item in progress.metric_provenance)
    assert {item.issue_code for item in progress.detected_issue_counts} == {"poor_depth", "poor_control"}
    squat = next(item for item in progress.exercise_comparisons if item.exercise_id == "bodyweight_squat")
    assert squat.has_comparison is True
    assert squat.baseline_movement_score == 80
    assert squat.latest_movement_score == 88
    assert squat.score_delta == 8
    assert squat.reps_delta == 2
    sit_to_stand = next(item for item in progress.exercise_comparisons if item.exercise_id == "sit_to_stand")
    assert sit_to_stand.has_comparison is False and sit_to_stand.score_delta is None
