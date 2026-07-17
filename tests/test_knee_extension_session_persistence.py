from sqlalchemy.orm import sessionmaker

from app.db.database import Base, create_database_engine
from app.schemas.analysis_schema import AnalysisResponse
from app.services.session_persistence_service import save_analysis_session


def test_knee_extension_session_uses_display_name(tmp_path):
    engine = create_database_engine(f"sqlite:///{(tmp_path / 'knee.db').as_posix()}")
    Base.metadata.create_all(engine)
    db = sessionmaker(bind=engine, expire_on_commit=False)()
    saved = save_analysis_session(AnalysisResponse(exercise="knee_extension", exercise_id="knee_extension", exercise_name="Knee Extension", total_reps=3, valid_reps=3, movement_score=84), db=db)
    assert saved.exercise_id == "knee_extension"
    assert saved.exercise_display_name == "Knee Extension"
    assert saved.total_reps == 3
