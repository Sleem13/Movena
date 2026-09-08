# Movena Backend

## Controlled staging

Copy values from `.env.staging.example` into the hosting provider's secret/environment settings; never commit a populated staging file. Staging startup refuses the default/short `SECRET_KEY`, wildcard or non-HTTPS CORS, disabled analysis auth, and public demo mode. Provider-style PostgreSQL URLs use Psycopg 3 while local development remains SQLite.

Use `/health` for liveness and `/ready` for database/artifact readiness. Reports and overlays require bearer auth or an unexpired signed link when protected analysis is enabled. See `docs/staging_deployment_strategy.md` and `docs/staging_artifact_storage_plan.md`.

FastAPI backend for the Movena movement-analysis API.

## Setup

Run these commands from the project root so the environment is not tied to a stale path. Use Python 3.12 for the project virtual environment:

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements-dev.txt
Copy-Item .env.example .env
.\scripts\start_backend.ps1 -Reload
```

If PowerShell activation is blocked, call the project interpreter directly:

```powershell
.\.venv\Scripts\python.exe -m pip install --upgrade pip
.\.venv\Scripts\python.exe -m pip install -r requirements-dev.txt
.\scripts\start_backend.ps1 -Reload
```

The startup script checks that `.venv` is Python 3.12 and prints the process holding the port if `8000` is already occupied. To run on another port:

```powershell
.\scripts\start_backend.ps1 -Port 8001 -Reload
```

Manual equivalent from `backend/`:

```powershell
..\.venv\Scripts\python.exe -m uvicorn app.main:app --env-file ..\.env --reload --host 127.0.0.1 --port 8000
```

The legacy entrypoint is also supported from `backend/`:

```powershell
uvicorn api.main:app --reload --host 127.0.0.1 --port 8000
```

## Test

```powershell
Set-Location ..
python -m pytest
```

Using `python -m pytest` avoids the Windows `pytest.exe` launcher retaining an absolute path to a deleted or moved virtual environment.
