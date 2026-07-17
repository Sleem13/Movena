import sys
from pathlib import Path

from fastapi.testclient import TestClient
from sqlalchemy.orm import sessionmaker

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "backend"))

from app.db.database import Base, create_database_engine, get_db
from app.main import app
from app.schemas.analysis_schema import AnalysisResponse
from app.services.session_persistence_service import save_analysis_session
from app.api.dependencies.auth import get_current_user
from types import SimpleNamespace


def test_list_detail_and_delete_saved_sessions(tmp_path):
    engine = create_database_engine(f"sqlite:///{(tmp_path / 'api.db').as_posix()}")
    Base.metadata.create_all(engine)
    factory = sessionmaker(bind=engine, expire_on_commit=False)
    db = factory()
    first = save_analysis_session(AnalysisResponse(
        exercise="bodyweight_squat", total_reps=3, movement_score=90,
        detected_issues=["poor_depth"], feedback=["Review depth."],
    ), db=db)
    save_analysis_session(AnalysisResponse(
        exercise="sit_to_stand", total_reps=2, movement_score=80,
    ), db=db)

    def override_db():
        session = factory()
        try:
            yield session
        finally:
            session.close()

    app.dependency_overrides[get_db] = override_db
    app.dependency_overrides[get_current_user] = lambda: SimpleNamespace(user_id="admin", role="admin")
    try:
        client = TestClient(app)
        listing = client.get("/api/v1/sessions?exercise_id=bodyweight_squat")
        assert listing.status_code == 200
        assert listing.json()["total"] == 1
        assert listing.json()["items"][0]["detected_issues"] == ["poor_depth"]

        detail = client.get(f"/api/v1/sessions/{first.session_id}")
        assert detail.status_code == 200
        assert detail.json()["feedback"] == ["Review depth."]
        assert len(detail.json()["metrics"]) == 5

        deleted = client.delete(f"/api/v1/sessions/{first.session_id}")
        assert deleted.status_code == 200
        assert client.get(f"/api/v1/sessions/{first.session_id}").status_code == 404
    finally:
        app.dependency_overrides.clear()
        db.close()
