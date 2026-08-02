"""Seed a development-only administrator from environment variables."""
from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "backend"))

from app.core.config import get_settings
from app.db.database import init_db
from app.services.admin_seed_service import seed_admin, seed_admin_from_environment, validate_admin_password


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
