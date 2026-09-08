"""Isolate repository-level tests from the caller's deployment environment."""

import os
import sys
from pathlib import Path

# These values must be assigned before adding/importing the backend application.
# Deliberately overwrite inherited staging/production values so collection is
# deterministic even when pytest is launched from a deployment-configured shell.
os.environ["APP_ENV"] = "test"
os.environ["SECRET_KEY"] = "test-secret-key-for-pytest-only-1234567890"
os.environ["CORS_ALLOWED_ORIGINS"] = "http://localhost:5173,http://127.0.0.1:5173"
os.environ["REQUIRE_AUTH_FOR_ANALYSIS"] = "false"
os.environ["ENABLE_PUBLIC_DEMO_MODE"] = "true"
os.environ["DATABASE_URL"] = "sqlite:///./test_movena.db"

BACKEND = Path(__file__).resolve().parents[1] / "backend"
_TEST_DATABASE_PATH = BACKEND.parent / "test_movena.db"
_TEST_DATABASE_PATH.unlink(missing_ok=True)
if str(BACKEND) not in sys.path:
    sys.path.insert(0, str(BACKEND))


def pytest_sessionfinish(session, exitstatus):
    """Close SQLite handles and remove this run's isolated test database."""
    del session, exitstatus
    database_module = sys.modules.get("app.db.database")
    if database_module is not None:
        database_module.engine.dispose()
    _TEST_DATABASE_PATH.unlink(missing_ok=True)
