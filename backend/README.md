# PhysioVision AI Backend

FastAPI backend for the Sprint 1 Squat Analyzer MVP.

## Setup

Run these commands from the project root so the environment is not tied to a stale path:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements-dev.txt
Set-Location backend
python -m uvicorn app.main:app --reload
```

## Test

```powershell
Set-Location ..
python -m pytest
```

Using `python -m pytest` avoids the Windows `pytest.exe` launcher retaining an absolute path to a deleted or moved virtual environment.
