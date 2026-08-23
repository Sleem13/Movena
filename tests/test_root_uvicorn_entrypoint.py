import subprocess
import sys
from pathlib import Path

from api.main import app


REPOSITORY_ROOT = Path(__file__).resolve().parents[1]


def test_root_uvicorn_entrypoint_exposes_fastapi_app():
    assert app.title == "PhysioVision AI"


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

    assert result.stdout.strip().splitlines()[-1] == "PhysioVision AI"
