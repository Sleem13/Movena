from sqlalchemy import select
from sqlalchemy.orm import sessionmaker

from app.db.database import Base, create_database_engine
from app.db.models import RecognitionEvent
from app.services.recognition_event_service import confirm_recognition_event, save_recognition_event


def test_recognition_event_persists_only_derived_audit_fields(tmp_path):
    engine = create_database_engine(f"sqlite:///{(tmp_path / 'recognition.db').as_posix()}")
    Base.metadata.create_all(engine)
    database = sessionmaker(bind=engine, expire_on_commit=False)()
    result = {
        "status": "uncertain",
        "model_id": "sequence_candidate",
        "suggested_exercise_id": "push_up",
        "confidence": 0.54,
        "confidence_threshold": 0.64,
        "analyzer_available": True,
    }
    row = save_recognition_event(
        result, source_type="video_upload", usable_pose_frames=42, db=database
    )
    assert row is not None
    stored = database.scalar(select(RecognitionEvent).where(RecognitionEvent.event_id == row.event_id))
    assert stored.abstained is True
    assert stored.usable_pose_frames == 42
    assert not hasattr(stored, "source_filename")
    assert not hasattr(stored, "stored_path")
    confirmed = confirm_recognition_event(row.event_id, "bodyweight_squat", db=database)
    assert confirmed.confirmed_exercise_id == "bodyweight_squat"
    assert confirmed.confirmed_at is not None
    database.close()
    engine.dispose()
