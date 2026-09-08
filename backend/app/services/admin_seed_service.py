"""Explicit administrator seeding for controlled development and staging use."""

from __future__ import annotations

import os
from collections.abc import Mapping
from uuid import uuid4

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.core.security import get_password_hash
from app.core.authorization import permissions_json_for_role
from app.db.database import SessionLocal
from app.db.models import User


def validate_admin_password(password: str) -> None:
    if len(password) < 8:
        raise ValueError("Administrator passwords must be at least 8 characters.")


def normalize_admin_username(username: str | None) -> str | None:
    if username is None:
        return None
    normalized = username.strip().lower()
    if not 3 <= len(normalized) <= 64:
        raise ValueError("Administrator usernames must be between 3 and 64 characters.")
    if not all(character.isalnum() or character in "._-" for character in normalized):
        raise ValueError("Administrator usernames may contain only letters, numbers, dots, hyphens, and underscores.")
    return normalized


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
            if existing.is_protected or existing.role == "super_admin":
                raise ValueError("The configured admin email belongs to a protected super-administrator account.")
            existing.password_hash = get_password_hash(password)
            existing.full_name = full_name
            existing.role = "admin"
            existing.permissions_json = permissions_json_for_role("admin")
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
                permissions_json=permissions_json_for_role("admin"),
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


def seed_super_admin(
    email: str,
    password: str,
    full_name: str | None,
    username: str | None = None,
    *,
    reset: bool = False,
    db: Session | None = None,
) -> tuple[User, bool]:
    """Provision the protected root account outside the public/admin APIs."""
    validate_admin_password(password)
    normalized_username = normalize_admin_username(username)
    owns_session = db is None
    session = db or SessionLocal()
    try:
        normalized_email = email.lower().strip()
        existing = session.scalar(select(User).where(User.email == normalized_email))
        if normalized_username:
            username_owner = session.scalar(
                select(User).where(func.lower(User.username) == normalized_username)
            )
            if username_owner and username_owner.email != normalized_email:
                raise ValueError("The configured super-admin username belongs to another account.")
        if existing and not reset:
            if existing.role != "super_admin" or not existing.is_protected:
                raise ValueError("The configured super-admin email belongs to an unprotected account; use --reset to promote it explicitly.")
            return existing, False
        user = existing or User(user_id=str(uuid4()), email=normalized_email, password_hash="")
        user.password_hash = get_password_hash(password)
        if normalized_username:
            user.username = normalized_username
        user.full_name = full_name
        user.role = "super_admin"
        user.permissions_json = permissions_json_for_role("super_admin")
        user.is_active = True
        user.is_verified = True
        user.account_status = "active"
        user.is_protected = True
        user.token_version = (user.token_version or 0) + (1 if existing else 0)
        if existing is None:
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


def seed_super_admin_from_environment(
    *,
    reset: bool = False,
    db: Session | None = None,
    environ: Mapping[str, str] | None = None,
) -> tuple[User, bool] | None:
    values = environ if environ is not None else os.environ
    enabled = values.get("SEED_SUPER_ADMIN_ON_START", "").strip().lower() in {"1", "true", "yes", "on"}
    if not enabled:
        return None
    email = values.get("SUPER_ADMIN_EMAIL", "").strip()
    password = values.get("SUPER_ADMIN_PASSWORD", "")
    name = values.get("SUPER_ADMIN_FULL_NAME", "Super Administrator")
    username = values.get("SUPER_ADMIN_USERNAME", "").strip() or None
    if not email or not password:
        raise ValueError("SUPER_ADMIN_EMAIL and SUPER_ADMIN_PASSWORD are required when SEED_SUPER_ADMIN_ON_START is enabled.")
    return seed_super_admin(email, password, name, username, reset=reset, db=db)
