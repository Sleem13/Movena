"""Database engine and session lifecycle configuration."""

from __future__ import annotations

from collections.abc import Generator
from pathlib import Path
from typing import Any

from sqlalchemy import create_engine, inspect, text
from sqlalchemy.engine import Engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from app.core.artifact_config import BACKEND_ROOT
from app.core.config import database_url_from_environment, normalize_database_url


DEFAULT_DATABASE_PATH = BACKEND_ROOT / "physiovision_dev.db"
DEFAULT_DATABASE_URL = f"sqlite:///{DEFAULT_DATABASE_PATH.as_posix()}"
DATABASE_URL = database_url_from_environment(DEFAULT_DATABASE_URL)
LATEST_SCHEMA_REVISION = "0006_coaching_follow_up"


class Base(DeclarativeBase):
    pass


def create_database_engine(database_url: str = DATABASE_URL) -> Engine:
    normalized_url = normalize_database_url(database_url)
    return create_engine(normalized_url, **_database_engine_options(normalized_url))


def _database_engine_options(database_url: str) -> dict[str, Any]:
    connect_args: dict[str, Any] = {}
    if database_url.startswith("sqlite"):
        connect_args["check_same_thread"] = False
    elif database_url.startswith("postgresql+psycopg://"):
        # Render/Neon/Supabase pooled PostgreSQL connections can reuse backend
        # sessions across clients, which conflicts with psycopg's auto-prepared
        # statement names during startup metadata checks.
        connect_args["prepare_threshold"] = None
    return {"connect_args": connect_args, "pool_pre_ping": True}


engine = create_database_engine()
SessionLocal = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False, class_=Session)


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def _legacy_username(email: str, existing: set[str]) -> str:
    local_part = email.partition("@")[0].strip().lower()
    base = "".join(character if character.isalnum() or character in "._-" else "_" for character in local_part)
    base = base.strip("._-") or "user"
    if len(base) < 3:
        base = f"user_{base}"
    base = base[:64]
    candidate = base
    suffix = 2
    while candidate.lower() in existing:
        marker = f"-{suffix}"
        candidate = f"{base[:64 - len(marker)]}{marker}"
        suffix += 1
    existing.add(candidate.lower())
    return candidate


def init_db(bind: Engine | None = None) -> None:
    from app.db import models  # noqa: F401 - registers model metadata
    target = bind or engine
    Base.metadata.create_all(target)
    if "users" in inspect(target).get_table_names():
        user_columns = {column["name"] for column in inspect(target).get_columns("users")}
        user_additions = {
            "username": "VARCHAR(64) NULL",
            "account_status": "VARCHAR(32) NOT NULL DEFAULT 'active'",
            "is_protected": "BOOLEAN NOT NULL DEFAULT false",
            "token_version": "INTEGER NOT NULL DEFAULT 0",
            "permissions_json": "TEXT NOT NULL DEFAULT '[]'",
            "email_verified_at": "TIMESTAMP NULL",
            "verification_token_hash": "VARCHAR(64) NULL",
            "verification_token_expires": "TIMESTAMP NULL",
            "verification_sent_at": "TIMESTAMP NULL",
            "reset_password_token_hash": "VARCHAR(64) NULL",
            "reset_password_expires": "TIMESTAMP NULL",
            "reset_password_sent_at": "TIMESTAMP NULL",
        }
        for column, definition in user_additions.items():
            if column not in user_columns:
                with target.begin() as connection:
                    connection.execute(text(f"ALTER TABLE users ADD COLUMN {column} {definition}"))
        # Backfill only missing permission snapshots. Existing role assignments are never changed.
        from app.core.authorization import ROLE_PERMISSIONS, permissions_json_for_role
        with target.begin() as connection:
            for role in ROLE_PERMISSIONS:
                connection.execute(
                    text("UPDATE users SET permissions_json = :permissions WHERE role = :role AND (permissions_json IS NULL OR permissions_json = '[]')"),
                    {"permissions": permissions_json_for_role(role), "role": role},
                )
            existing_usernames = {
                str(row.username).lower()
                for row in connection.execute(text("SELECT username FROM users WHERE username IS NOT NULL AND username <> ''"))
            }
            legacy_users = connection.execute(
                text("SELECT user_id, email FROM users WHERE username IS NULL OR username = '' ORDER BY user_id")
            ).mappings()
            for legacy_user in legacy_users:
                connection.execute(
                    text("UPDATE users SET username = :username WHERE user_id = :user_id"),
                    {
                        "username": _legacy_username(str(legacy_user["email"]), existing_usernames),
                        "user_id": legacy_user["user_id"],
                    },
                )
            connection.execute(text("CREATE UNIQUE INDEX IF NOT EXISTS ix_users_verification_token_hash ON users (verification_token_hash)"))
            connection.execute(text("CREATE UNIQUE INDEX IF NOT EXISTS ix_users_reset_password_token_hash ON users (reset_password_token_hash)"))
            connection.execute(text("CREATE UNIQUE INDEX IF NOT EXISTS ix_users_username ON users (username)"))
    # Development-only compatibility migration until versioned Alembic migrations are introduced.
    if target.dialect.name == "sqlite" and "analysis_sessions" in inspect(target).get_table_names():
        columns = {column["name"] for column in inspect(target).get_columns("analysis_sessions")}
        additions = {
            "patient_id": "VARCHAR(36) NULL",
            "plan_item_id": "VARCHAR(36) NULL",
            "owner_user_id": "VARCHAR(36) NULL",
            "created_by_user_id": "VARCHAR(36) NULL",
        }
        for column, definition in additions.items():
            if column not in columns:
                with target.begin() as connection:
                    connection.execute(text(f"ALTER TABLE analysis_sessions ADD COLUMN {column} {definition}"))
        with target.begin() as connection:
            connection.execute(text(
                "CREATE INDEX IF NOT EXISTS ix_analysis_sessions_plan_item_id "
                "ON analysis_sessions (plan_item_id)"
            ))
    if target.dialect.name == "sqlite" and "patient_profiles" in inspect(target).get_table_names():
        columns = {column["name"] for column in inspect(target).get_columns("patient_profiles")}
        additions = {
            "user_id": "VARCHAR(36) NULL",
            "preferred_locale": "VARCHAR(8) NOT NULL DEFAULT 'ar'",
            "timezone_name": "VARCHAR(64) NOT NULL DEFAULT 'Africa/Cairo'",
        }
        for column, definition in additions.items():
            if column not in columns:
                with target.begin() as connection:
                    connection.execute(text(f"ALTER TABLE patient_profiles ADD COLUMN {column} {definition}"))
        with target.begin() as connection:
            connection.execute(text("CREATE UNIQUE INDEX IF NOT EXISTS ux_patient_profiles_user_id ON patient_profiles (user_id)"))
    if target.dialect.name == "sqlite" and "exercise_plan_items" in inspect(target).get_table_names():
        columns = {column["name"] for column in inspect(target).get_columns("exercise_plan_items")}
        additions = {
            "duration_minutes": "INTEGER NULL",
            "rest_interval_seconds": "INTEGER NULL",
            "tempo": "VARCHAR(64) NULL",
            "precautions": "TEXT NULL",
            "target_rom_degrees": "FLOAT NULL",
            "target_score": "FLOAT NULL",
            "schedule_days_json": "TEXT NOT NULL DEFAULT '[]'",
            "requested_media_upload": "BOOLEAN NOT NULL DEFAULT false",
            "requires_ai_analysis": "BOOLEAN NOT NULL DEFAULT false",
            "status": "VARCHAR(24) NOT NULL DEFAULT 'active'",
        }
        for column, definition in additions.items():
            if column not in columns:
                with target.begin() as connection:
                    connection.execute(text(f"ALTER TABLE exercise_plan_items ADD COLUMN {column} {definition}"))
        with target.begin() as connection:
            connection.execute(text(
                "CREATE INDEX IF NOT EXISTS ix_exercise_plan_items_status "
                "ON exercise_plan_items (status)"
            ))
    if target.dialect.name == "sqlite" and "adherence_entries" in inspect(target).get_table_names():
        columns = {column["name"] for column in inspect(target).get_columns("adherence_entries")}
        additions = {
            "fatigue": "INTEGER NULL",
            "analysis_session_id": "VARCHAR(36) NULL",
        }
        for column, definition in additions.items():
            if column not in columns:
                with target.begin() as connection:
                    connection.execute(text(f"ALTER TABLE adherence_entries ADD COLUMN {column} {definition}"))
        with target.begin() as connection:
            connection.execute(text(
                "CREATE INDEX IF NOT EXISTS ix_adherence_entries_analysis_session_id "
                "ON adherence_entries (analysis_session_id)"
            ))


def verify_production_schema(bind: Engine | None = None) -> None:
    """Production schema changes must be applied by Alembic before startup."""
    target = bind or engine
    tables = set(inspect(target).get_table_names())
    if "alembic_version" not in tables:
        raise RuntimeError("Production database is not migration-managed. Run 'alembic upgrade head'.")
    with target.connect() as connection:
        version = connection.execute(text("SELECT version_num FROM alembic_version")).scalar()
    if version != LATEST_SCHEMA_REVISION:
        raise RuntimeError(f"Production database migration is not current (found {version!r}).")
