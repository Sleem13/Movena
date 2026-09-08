import os
import subprocess
import sys
from pathlib import Path

from api.main import app


REPOSITORY_ROOT = Path(__file__).resolve().parents[1]


def test_root_uvicorn_entrypoint_exposes_fastapi_app():
    assert app.title == "Movena"


def test_render_root_uvicorn_entrypoint_exposes_fastapi_app():
    result = subprocess.run(
        [
            sys.executable,
            "-c",
            "from app.main import app; print(app.title)",
        ],
        cwd=REPOSITORY_ROOT,
        check=True,
        capture_output=True,
        text=True,
    )

    assert result.stdout.strip().splitlines()[-1] == "Movena"


def test_render_staging_starts_without_optional_ml_runtimes(tmp_path):
    environment = os.environ.copy()
    environment.update(
        {
            "APP_ENV": "staging",
            "DATABASE_URL": f"sqlite:///{(tmp_path / 'render_startup_test.db').as_posix()}",
            "CORS_ALLOWED_ORIGINS": "https://app.example.com",
            "SECRET_KEY": "render-startup-test-secret-key-longer-than-32-characters",
            "REQUIRE_AUTH_FOR_ANALYSIS": "true",
            "ENABLE_PUBLIC_DEMO_MODE": "false",
            "ENABLE_SUBJECT_CONTINUITY_GUARD": "true",
            "ENABLE_ML_SECOND_OPINION": "false",
                "ENABLE_EXERCISE_RECOGNITION": "false",
                "EMAIL_DELIVERY_MODE": "smtp",
                "EMAIL_FROM": "no-reply@example.com",
                "SMTP_HOST": "smtp.example.com",
                "FRONTEND_URL": "https://app.example.com",
                "CLINICAL_ORGANIZATION_NAME": "Example Rehabilitation Organization",
                "CLINICAL_ESCALATION_CONTACT": "+20-000-000-0000",
        }
    )
    script = """
import builtins
original_import = builtins.__import__
def render_import(name, *args, **kwargs):
    if name == 'torch' or name.startswith('torch.') or name == 'xgboost' or name.startswith('xgboost.'):
        raise ImportError(f'No module named {name!r}')
    return original_import(name, *args, **kwargs)
builtins.__import__ = render_import
from app.main import app
print(app.title)
"""

    result = subprocess.run(
        [sys.executable, "-c", script],
        cwd=REPOSITORY_ROOT,
        env=environment,
        check=True,
        capture_output=True,
        text=True,
    )

    assert result.stdout.strip().splitlines()[-1] == "Movena"
