import sys
from pathlib import Path

from sqlalchemy import inspect
from sqlalchemy.orm import sessionmaker

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "backend"))

from app.db.database import Base, create_database_engine
from app.db import models  # noqa: F401


def test_database_initializes_all_session_tables(tmp_path: Path):
    engine = create_database_engine(f"sqlite:///{(tmp_path / 'test.db').as_posix()}")
    Base.metadata.create_all(engine)
    tables = set(inspect(engine).get_table_names())
    assert {"analysis_sessions", "session_metrics", "uploaded_media", "detected_issues"} <= tables
    sessionmaker(bind=engine)().close()
