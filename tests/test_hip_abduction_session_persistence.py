from sqlalchemy.orm import sessionmaker

from app.db.database import Base, create_database_engine
from app.schemas.analysis_schema import AnalysisResponse
from app.services.session_persistence_service import save_analysis_session


def test_hip_abduction_session_display_name(tmp_path):
    engine = create_database_engine(f"sqlite:///{(tmp_path / 'hip.db').as_posix()}"); Base.metadata.create_all(engine)
    db = sessionmaker(bind=engine, expire_on_commit=False)()
    saved = save_analysis_session(AnalysisResponse(exercise="hip_abduction", exercise_id="hip_abduction", exercise_name="Hip Abduction", total_reps=3, valid_reps=3, movement_score=84, average_hip_abduction_angle=30), db=db)
    assert saved.exercise_id == "hip_abduction"
    assert saved.exercise_display_name == "Hip Abduction"
    assert any(metric.metric_name == "average_hip_abduction_angle" for metric in saved.metrics)
