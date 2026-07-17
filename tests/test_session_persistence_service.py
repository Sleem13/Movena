import sys
from pathlib import Path

from sqlalchemy.orm import sessionmaker

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "backend"))

from app.db.database import Base, create_database_engine
from app.schemas.analysis_schema import AnalysisConfidence, AnalysisResponse, PoseQuality
from app.services.session_persistence_service import save_analysis_session


def database(tmp_path):
    engine = create_database_engine(f"sqlite:///{(tmp_path / 'sessions.db').as_posix()}")
    Base.metadata.create_all(engine)
    return sessionmaker(bind=engine, expire_on_commit=False)()


def pose():
    return PoseQuality(
        score=0.8, level="high", total_frames=60, pose_detected_frames=55,
        pose_detection_rate=0.92, average_visibility=0.85,
        critical_landmark_visibility=0.82, missing_critical_landmark_rate=0,
        low_confidence_frames=2,
    )


def test_save_successful_squat_session_with_metrics_and_issues(tmp_path):
    db = database(tmp_path)
    response = AnalysisResponse(
        total_reps=3, movement_score=87, average_knee_angle=100,
        detected_issues=["poor_depth"], pose_quality=pose(),
        analysis_confidence=AnalysisConfidence(score=0.78, level="medium"),
    )
    saved = save_analysis_session(response, "squat.mp4", {"size_bytes": 123}, db)
    assert saved.exercise_id == "bodyweight_squat"
    assert saved.total_reps == 3
    assert len(saved.metrics) == 5
    assert saved.detected_issue_rows[0].issue_code == "poor_depth"
    assert saved.uploaded_media[0].stored_path is None


def test_save_rejected_and_sit_to_stand_sessions(tmp_path):
    db = database(tmp_path)
    rejected = save_analysis_session(AnalysisResponse(
        status="rejected", error_code="INVALID_SQUAT_VIDEO", movement_score=None,
        detected_issues=["no_valid_squat_detected"],
    ), db=db)
    chair = save_analysis_session(AnalysisResponse(
        exercise="sit_to_stand", total_reps=2, movement_score=82,
    ), db=db)
    assert rejected.status == "rejected" and rejected.movement_score is None
    assert chair.exercise_display_name == "Sit-to-Stand"
