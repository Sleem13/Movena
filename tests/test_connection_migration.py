from pathlib import Path

from alembic import command
from alembic.config import Config
from sqlalchemy import create_engine, inspect, text

from app.db.models import Base, User
from sqlalchemy.orm import Session


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
            with Session(engine) as session:
                session.add(User(user_id="patient-without-profile", username="legacy.patient", email="legacy@example.com", password_hash="hash", full_name="Legacy Patient", role="patient"))
                session.commit()
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
            assert connection.scalar(text("SELECT version_num FROM alembic_version")) == "0010_identity_projection"
            assert "identity_owner" in {c["name"] for c in inspect(engine).get_columns("users")}
            assert "internal_principal_nonces" in inspect(engine).get_table_names()
            if existing:
                assert connection.execute(text("SELECT assignment_id, status, source FROM therapist_patient_assignments")).one() == ("old", "active", "legacy")
                assert connection.execute(text("SELECT user_id, display_name FROM patient_profiles WHERE user_id = 'patient-without-profile'")).one() == ("patient-without-profile", "Legacy Patient")
        command.upgrade(cfg, "head")
        engine.dispose()
