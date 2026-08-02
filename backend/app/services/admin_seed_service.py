"""Explicit administrator seeding for controlled development and staging use."""

from __future__ import annotations

import os
from collections.abc import Mapping
from uuid import uuid4

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.security import get_password_hash
from app.db.database import SessionLocal
from app.db.models import User


def validate_admin_password(password: str) -> None:
    if len(password) < 8:
        raise ValueError("ADMIN_PASSWORD must be at least 8 characters.")


def seed_admin(
    email: str,
    password: str,
    full_name: str | None,
    *,
    reset: bool = False,
    db: Session | None = None,
) -> tuple[User, bool]:
    validate_admin_password(password)
    owns_session = db is None
    session = db or SessionLocal()
    try:
        existing = session.scalar(select(User).where(User.email == email.lower().strip()))
        if existing and not reset:
            return existing, False
        if existing:
            existing.password_hash = get_password_hash(password)
            existing.full_name = full_name
            existing.role = "admin"
            existing.is_active = True
            existing.is_verified = True
            user = existing
        else:
            user = User(
                user_id=str(uuid4()),
                email=email.lower().strip(),
                password_hash=get_password_hash(password),
                full_name=full_name,
                role="admin",
                is_active=True,
                is_verified=True,
            )
            session.add(user)
        session.commit()
        session.refresh(user)
        return user, True
    finally:
        if owns_session:
            session.close()


def seed_admin_from_environment(
    *,
    reset: bool = False,
    db: Session | None = None,
    environ: Mapping[str, str] | None = None,
) -> tuple[User, bool] | None:
    values = environ if environ is not None else os.environ
    enabled = values.get("SEED_ADMIN_ON_START", "").strip().lower() in {"1", "true", "yes", "on"}
    if not enabled:
        return None
    email = values.get("ADMIN_EMAIL", "").strip()
    password = values.get("ADMIN_PASSWORD", "")
    name = values.get("ADMIN_FULL_NAME", "Development Admin")
    if not email or not password:
        raise ValueError("ADMIN_EMAIL and ADMIN_PASSWORD are required when SEED_ADMIN_ON_START is enabled.")
    return seed_admin(email, password, name, reset=reset, db=db)
