from pathlib import Path

from alembic import command
from alembic.config import Config
from sqlalchemy import create_engine, inspect, text

from app.db.models import Base


def test_fresh_and_existing_connection_migration(tmp_path, monkeypatch):
    root = Path(__file__).resolve().parents[1]
    for existing in (False, True):
        url = f"sqlite:///{(tmp_path / ('existing.db' if existing else 'fresh.db')).as_posix()}"
        monkeypatch.setenv("DATABASE_URL", url)
        engine = create_engine(url)
        cfg = Config(str(root / "alembic.ini"))
        cfg.set_main_option("script_location", str(root / "backend/alembic"))
        if existing:
            Base.metadata.create_all(engine)
            with engine.begin() as connection:
                connection.execute(text("DROP TABLE care_invitations"))
                for name in ("source", "ended_at", "ended_by_user_id", "end_reason"):
                    connection.execute(text(f"ALTER TABLE therapist_patient_assignments DROP COLUMN {name}"))
                connection.execute(text("INSERT INTO therapist_patient_assignments (assignment_id, therapist_user_id, patient_id, status, assigned_at) VALUES ('old', 'therapist', 'patient', 'active', '2026-01-01')"))
            command.stamp(cfg, "0007_exercise_response")
        command.upgrade(cfg, "head")
        assert "care_invitations" in inspect(engine).get_table_names()
        assert {"source", "ended_at", "end_reason"} <= {c["name"] for c in inspect(engine).get_columns("therapist_patient_assignments")}
        with engine.connect() as connection:
            assert connection.scalar(text("SELECT version_num FROM alembic_version")) == "0008_care_connections"
            if existing:
                assert connection.execute(text("SELECT assignment_id, status, source FROM therapist_patient_assignments")).one() == ("old", "active", "legacy")
        command.upgrade(cfg, "head")
        engine.dispose()
