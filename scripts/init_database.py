"""Initialize the local PhysioVision AI analysis-session database."""

from __future__ import annotations

import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "backend"))

from app.db.database import DATABASE_URL, init_db


def main() -> int:
    try:
        init_db()
    except Exception as exc:
        print(f"Database initialization failed: {exc}", file=sys.stderr)
        return 1
    safe_url = DATABASE_URL.split("@")[-1] if "@" in DATABASE_URL else DATABASE_URL
    print(f"Database tables initialized: {safe_url}")
    print("This database stores analysis metadata only and is not a production patient record system.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
