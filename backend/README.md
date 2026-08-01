# PhysioVision AI Backend

## Controlled staging

Copy values from `.env.staging.example` into the hosting provider's secret/environment settings; never commit a populated staging file. Staging startup refuses the default/short `SECRET_KEY`, wildcard or non-HTTPS CORS, disabled analysis auth, and public demo mode. Provider-style PostgreSQL URLs use Psycopg 3 while local development remains SQLite.

Use `/health` for liveness and `/ready` for database/artifact readiness. Reports and overlays require bearer auth or an unexpired signed link when protected analysis is enabled. See `docs/staging_deployment_strategy.md` and `docs/staging_artifact_storage_plan.md`.

FastAPI backend for the Sprint 1 Squat Analyzer MVP.

## Setup

Run these commands from the project root so the environment is not tied to a stale path:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements-dev.txt
python -m uvicorn api.main:app --reload --host 127.0.0.1 --port 8000
```

## Test

```powershell
Set-Location ..
python -m pytest
```

Using `python -m pytest` avoids the Windows `pytest.exe` launcher retaining an absolute path to a deleted or moved virtual environment.
