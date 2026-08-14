import sys
from pathlib import Path

from sqlalchemy import inspect
from sqlalchemy.orm import sessionmaker

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "backend"))

from app.db import database, models  # noqa: F401
from app.db.database import Base, create_database_engine


def test_database_initializes_all_session_tables(tmp_path: Path):
    engine = create_database_engine(f"sqlite:///{(tmp_path / 'test.db').as_posix()}")
    Base.metadata.create_all(engine)
    tables = set(inspect(engine).get_table_names())
    assert {"analysis_sessions", "session_metrics", "uploaded_media", "detected_issues"} <= tables
    sessionmaker(bind=engine)().close()


def test_create_database_engine_disables_psycopg_prepared_statements(monkeypatch):
    captured: dict[str, object] = {}

    def fake_create_engine(database_url: str, **options):
        captured["database_url"] = database_url
        captured["options"] = options
        return object()

    monkeypatch.setattr(database, "create_engine", fake_create_engine)

    database.create_database_engine("postgres://user:pass@host/db?sslmode=require")

    assert captured["database_url"] == "postgresql+psycopg://user:pass@host/db?sslmode=require"
    assert captured["options"] == {
        "connect_args": {"prepare_threshold": None},
        "pool_pre_ping": True,
    }
