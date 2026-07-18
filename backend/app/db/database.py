"""Database engine and session lifecycle configuration."""

from __future__ import annotations

import os
from collections.abc import Generator
from pathlib import Path

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
    connect_args = {"check_same_thread": False} if database_url.startswith("sqlite") else {}
    return create_engine(database_url, connect_args=connect_args, pool_pre_ping=True)


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
