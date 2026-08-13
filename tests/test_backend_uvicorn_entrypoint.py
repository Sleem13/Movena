import subprocess
import sys
from pathlib import Path


REPOSITORY_ROOT = Path(__file__).resolve().parents[1]


def test_backend_directory_uvicorn_entrypoint_exposes_fastapi_app():
    result = subprocess.run(
        [
            sys.executable,
            "-c",
            "from api.main import app; print(app.title)",
        ],
        cwd=REPOSITORY_ROOT / "backend",
        check=True,
        capture_output=True,
        text=True,
    )

    assert result.stdout.strip().splitlines()[-1] == "PhysioVision AI"
