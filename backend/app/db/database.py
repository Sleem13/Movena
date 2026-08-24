"""Database engine and session lifecycle configuration."""

from __future__ import annotations

import os
from collections.abc import Generator
from pathlib import Path
from typing import Any

from sqlalchemy import create_engine, inspect, text
from sqlalchemy.engine import Engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from app.core.artifact_config import BACKEND_ROOT
from app.core.config import normalize_database_url


DEFAULT_DATABASE_PATH = BACKEND_ROOT / "physiovision_dev.db"
DEFAULT_DATABASE_URL = f"sqlite:///{DEFAULT_DATABASE_PATH.as_posix()}"
DATABASE_URL = normalize_database_url(os.getenv("DATABASE_URL", DEFAULT_DATABASE_URL))


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


def init_db(bind: Engine | None = None) -> None:
    from app.db import models  # noqa: F401 - registers model metadata
    target = bind or engine
    Base.metadata.create_all(target)
    if "users" in inspect(target).get_table_names():
        user_columns = {column["name"] for column in inspect(target).get_columns("users")}
        user_additions = {
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
            connection.execute(text("CREATE UNIQUE INDEX IF NOT EXISTS ix_users_verification_token_hash ON users (verification_token_hash)"))
            connection.execute(text("CREATE UNIQUE INDEX IF NOT EXISTS ix_users_reset_password_token_hash ON users (reset_password_token_hash)"))
    # Development-only compatibility migration until versioned Alembic migrations are introduced.
    if target.dialect.name == "sqlite" and "analysis_sessions" in inspect(target).get_table_names():
        columns = {column["name"] for column in inspect(target).get_columns("analysis_sessions")}
        if "patient_id" not in columns:
            with target.begin() as connection:
                connection.execute(text("ALTER TABLE analysis_sessions ADD COLUMN patient_id VARCHAR(36)"))
        for column in ("owner_user_id", "created_by_user_id"):
            if column not in columns:
                with target.begin() as connection:
                    connection.execute(text(f"ALTER TABLE analysis_sessions ADD COLUMN {column} VARCHAR(36)"))
