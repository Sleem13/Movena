"""Seed a development-only administrator from environment variables."""
from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path
from uuid import uuid4

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "backend"))

from sqlalchemy import select
from app.core.config import get_settings
from app.core.security import get_password_hash
from app.db.database import SessionLocal, init_db
from app.db.models import User


def validate_admin_password(password: str) -> None:
    if len(password) < 14 or not any(c.isupper() for c in password) or not any(c.islower() for c in password) or not any(c.isdigit() for c in password):
        raise ValueError("ADMIN_PASSWORD must be at least 14 characters and include upper, lower, and numeric characters.")


def seed_admin(email: str, password: str, full_name: str | None, *, reset: bool = False, db=None) -> tuple[User, bool]:
    validate_admin_password(password)
    owns = db is None
    session = db or SessionLocal()
    try:
        existing = session.scalar(select(User).where(User.email == email.lower().strip()))
        if existing and not reset:
            return existing, False
        if existing:
            existing.password_hash = get_password_hash(password)
            existing.full_name = full_name
            existing.role = "admin"; existing.is_active = True; existing.is_verified = True
            user = existing
        else:
            user = User(user_id=str(uuid4()), email=email.lower().strip(), password_hash=get_password_hash(password),
                        full_name=full_name, role="admin", is_active=True, is_verified=True)
            session.add(user)
        session.commit(); session.refresh(user)
        return user, True
    finally:
        if owns: session.close()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--reset", action="store_true")
    args = parser.parse_args()
    if get_settings().app_env == "production":
        print("Refusing to seed a development admin in production.", file=sys.stderr); return 2
    email = os.getenv("ADMIN_EMAIL", "")
    password = os.getenv("ADMIN_PASSWORD", "")
    name = os.getenv("ADMIN_FULL_NAME", "Development Admin")
    if not email or not password:
        print("Set ADMIN_EMAIL and ADMIN_PASSWORD before running this script.", file=sys.stderr); return 2
    init_db()
    try:
        user, changed = seed_admin(email, password, name, reset=args.reset)
    except ValueError as exc:
        print(str(exc), file=sys.stderr); return 2
    print(f"Development admin {'created/updated' if changed else 'already exists'}: {user.email} ({user.user_id})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
