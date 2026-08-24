"""Provision the protected PhysioVision super-administrator account."""
from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "backend"))

from app.db.database import init_db
from app.services.admin_seed_service import seed_super_admin


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--reset", action="store_true", help="Explicitly promote/reset an account with the configured email.")
    args = parser.parse_args()
    email = os.getenv("SUPER_ADMIN_EMAIL", "").strip()
    password = os.getenv("SUPER_ADMIN_PASSWORD", "")
    name = os.getenv("SUPER_ADMIN_FULL_NAME", "Super Administrator")
    if not email or not password:
        print("Set SUPER_ADMIN_EMAIL and SUPER_ADMIN_PASSWORD before running this script.", file=sys.stderr)
        return 2
    init_db()
    try:
        user, changed = seed_super_admin(email, password, name, reset=args.reset)
    except ValueError as exc:
        print(str(exc), file=sys.stderr)
        return 2
    print(f"Protected super administrator {'created/updated' if changed else 'already exists'}: {user.email} ({user.user_id})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
