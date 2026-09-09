# Sprint 1.5 Review Report

Review date: 2026-07-10  
Reviewed workspace: project checkout

## 1. Executive Summary

Movena is **Conditionally Ready after local environment reset and dependency installation**. The repository has a coherent squat-focused FastAPI backend, a matching React frontend, separated camera and sensor dataset pipelines, synthetic unit tests, safety-oriented wording, and correct raw/processed data ignore rules. The frontend production build and isolated core-logic checks pass.

Two conditions prevent an unconditional readiness decision in this checkout:

1. **Environment issue: broken/mixed virtual environment paths.** Pandas cannot import `dateutil.tz`, while the `pytest.exe` launcher points to an obsolete external interpreter. The active environment is incomplete and inconsistent with the repository requirements, so full test collection and FastAPI startup cannot be trusted until it is replaced.
2. The raw UCI, Kaggle, custom-video, and sample-video folders contain no files other than `.gitkeep`, so real dataset preparation and end-to-end video analysis cannot be validated here.

This differs from the previously reported machine/path where the UCI and Kaggle folders had files. Because raw data is intentionally ignored by Git, that difference is expected when moving between workspaces, but it must be resolved locally before data-dependent validation.

No model was trained, no major feature was added, and the current architecture was preserved.

## 2. What Was Reviewed

- Root structure, naming, imports, path assumptions, Git status, and `.gitignore`.
- `backend/`, including startup composition, routes, schemas, pose estimation, angle calculation, squat analysis, feedback, upload handling, logging, and tests.
- `frontend/`, including package configuration, API client, upload/loading/error states, result-field mapping, and production build.
- `data/`, expected raw/processed/sample structure, current file availability, and privacy/large-file ignore rules.
- Dataset scripts: structure validation, UCI preparation, sensor features, video landmarks, angle features, and squat dataset preparation.
- Root and backend tests, including whether they rely on raw datasets.
- Requested documentation files and consistency with the implemented squat-only MVP.
- Python and frontend dependency declarations and the active runtime state.
- The `PysioVision` versus `Movena` spelling and space/hyphen path concern.

## 3. Current Project Status

| Area | Status | Notes |
|---|---|---|
| Repository structure | Ready | Clear backend/frontend/data/docs/scripts/tests separation. Expected folders exist. |
| Git data protection | Ready | Raw data and generated CSV/JSON/Parquet outputs are ignored; `.gitkeep` files remain tracked. Local sample metadata is now explicitly ignored. |
| Dataset folder validation | Ready | `python scripts/check_dataset_structure.py` exits 0. Validator now includes documented `uco_physical_rehab`. |
| Raw dataset availability | Not Ready | Current checkout has zero non-placeholder files in UCI, Kaggle, custom-video, and future dataset folders. |
| Sensor pipeline code | Partial | CLI, CSV/TXT/DATA discovery, metadata columns, missing-value handling, window features, and expected outputs exist. Real UCI schema validation is blocked by absent data. |
| Camera pipeline code | Partial | Empty input and missing MediaPipe handling are clear. No local video exists for landmark/angle end-to-end validation. |
| Backend implementation | Partial | Health and squat routes, services, response schema, logging, cleanup, and disclaimer exist. Startup is blocked in the active environment by missing FastAPI. |
| Frontend implementation | Ready | Upload, loading, error, and results flows match backend fields. `VITE_API_BASE_URL` is configurable. Production build passes. |
| Automated tests | Partial | Tests use synthetic/dummy data and do not require raw datasets. Full suite is blocked by the active Python environment; isolated core checks pass. |
| Documentation | Ready | Core documents exist, medical limitations are explicit, implemented scope is clarified as squat-only, and Sprint 2 is now documented. |
| Sprint 2 start | Partial | Development can begin after environment repair; real-video validation data is needed before Sprint 2 acceptance. |

## 4. Dataset Pipeline Status

### Folder validation

`python scripts/check_dataset_structure.py` completed successfully with exit code 0. All expected folders exist. It correctly reports raw dataset folders as empty rather than treating folder existence as proof of dataset availability.

The validator was missing `data/raw/uco_physical_rehab/` even though the folder and selection documentation existed. This was fixed in the validator, docs, and structure test.

### Raw datasets available

In this reviewed checkout:

- `data/raw/squat_kaggle/`: empty except `.gitkeep`.
- `data/raw/uci_physical_therapy_exercises/`: empty except `.gitkeep`.
- `data/raw/custom_videos/`: empty except placeholders.
- Future dataset folders: empty except placeholders.
- `data/samples/`: no videos.

The earlier statement that UCI and Kaggle contain files applies to a different local workspace or has become stale. Raw files are deliberately not transferred through Git.

### Processed outputs

No generated landmark, angle, UCI processed-row, or sensor-window output is present. Only `.gitkeep` files exist in processed folders.

### UCI pipeline

- `prepare_uci_physical_therapy_dataset.py` supports `.csv`, `.txt`, and `.data`, recursive discovery, delimiter fallback, normalized columns, inferred path metadata, missing-value reporting, CLI paths, and the documented output path.
- With a compatible pandas runtime and no data, it exits 1 with a helpful manual-download message.
- `extract_sensor_features.py` validates window arguments and required metadata, groups by source metadata, prevents crossing file/exercise boundaries, calculates mean/std/min/max/median/energy/range/RMS, and writes the expected CSV.
- With no processed input, it exits 1 with a helpful missing-file message.
- A synthetic six-row input produced two expected windows successfully in an isolated compatible runtime.
- Actual UCI column semantics, path-label inference, and structural missing values remain unverified until the real dataset is restored.

### Camera pipeline

- `extract_landmarks_from_videos.py` supports Windows paths, configurable input/output, common video formats, timestamps, labels, source metadata, failure CSV logging, and delayed OpenCV/MediaPipe imports with installation guidance.
- With empty input folders it exits 1 and clearly asks for local videos.
- `create_angle_features.py` resolves backend imports from the repository location, normalizes landmark input, calculates bilateral knee/hip/ankle and trunk angles, and writes to `data/processed/angle_features/`.
- With no landmarks it exits 1 with a clear message.
- End-to-end landmark extraction was not run because no input video exists.

## 5. Backend Status

Implemented:

- FastAPI application composition with CORS for documented local frontend origins.
- `GET /health` route returning status, project, and version.
- `POST /api/v1/analyze/squat` multipart upload route.
- Extension validation, empty-file rejection, temporary storage, and cleanup.
- Lazy OpenCV/MediaPipe imports and pose-specific error messages.
- CPU-oriented MediaPipe Pose configuration (`model_complexity=1`, no segmentation).
- Modular pose, angle, squat-rule, feedback, schema, logging, and file utilities.
- Rule-based repetition count, movement flags, score, limitations, and feedback.
- Medical disclaimer included in every successful response through the `feedback` list, with additional clinical limitations in `limitations`.

Not fully verified or missing:

- FastAPI startup and live `/health` response could not execute in the active Python environment because FastAPI is not installed there.
- No API route tests cover health, invalid extension, empty upload, no-pose video, cleanup, or response schema.
- No real-video endpoint integration test exists.
- Upload size is not capped; this is an important hardening item before exposing the service beyond local development.
- CORS origins are fixed for local development rather than environment-configurable.

The backend contains no hardcoded absolute project path. Its temporary upload path is relative to the backend working directory documented in the README.

Environment declaration review: root `requirements.txt` now includes the backend runtime requirements, while `requirements-dev.txt` adds pytest for development/testing. `backend/requirements.txt` pins FastAPI 0.116.1, Uvicorn 0.35.0, OpenCV 4.11.0.86, MediaPipe 0.10.21, NumPy 1.26.4, pandas 2.2.3, python-dateutil 2.9.0.post0, Pydantic 2.11.7, and python-multipart 0.0.20. `requirements-dev.txt` pins pytest 8.4.1. This is intended for Python 3.11 and is appropriate for the CPU-oriented prototype, but the exact clean install must still be verified on the user's Windows machine. The reviewed active interpreter was Python 3.11.0 but did not contain these pinned versions, so it was not a valid compatibility test.

## 6. Frontend Status

Implemented and verified:

- React/Vite source structure with home, upload, and result views.
- Configurable API base URL through `VITE_API_BASE_URL`, with documented local fallback.
- Multipart call to `/api/v1/analyze/squat`.
- File selection, disabled submit, loading state, backend-detail error display, and retry flow.
- Result components consume the backend's `movement_score`, `total_reps`, angle, issue, feedback, summary, and limitation fields.
- `npm.cmd run build` passes with Vite 6.4.3.

Gaps:

- No frontend unit/component tests or lint script.
- No verified live frontend-to-backend request in this environment.
- Both `pnpm-lock.yaml` and an untracked `package-lock.json` are present. The team should choose one package manager before committing another lockfile.

PowerShell blocked `npm run build` because script execution disabled `npm.ps1`; using `npm.cmd run build` works without changing execution policy.

## 7. Testing Status

Requested root command: `python -m pytest`

Result in the active environment: collection failed. Eight tests were collected before interruption, one pandas-dependent test module was skipped, and backend collection failed because the installed Pydantic/`annotated-types` packages are inconsistent. The same environment also lacks FastAPI and MediaPipe, and pandas cannot import because `dateutil.tz` is missing. This environment does not match the pinned backend requirements.

Launcher inspection confirms the mixed-environment diagnosis: the current shell resolves Python and its first pytest launcher under an external virtual environment, while the reported fatal pytest launcher embeds an older external path. Neither is the required project-local `.venv\Scripts\python.exe`.

Secondary isolated checks using a compatible bundled runtime:

- 9 backend pure test functions passed (angle and squat-analysis logic).
- Dataset structure assertion passed.
- Synthetic sliding-window sensor feature case passed.
- Python `compileall` passed for `backend`, `scripts`, and `tests`.

Existing tests correctly avoid real raw datasets and large files. Critical missing tests are API health/upload errors, temporary-file cleanup, empty landmark analysis, landmark CSV-to-angle integration, same-name input video collision behavior, and frontend API/error rendering.

## 8. Documentation Status

| Document | Status | Review note |
|---|---|---|
| `README.md` | Ready | Setup, API, dataset commands, limitations, disclaimer, and Sprint Status exist. Environment rebuild is now explicit. |
| `data/README.md` | Ready | Separates raw, processed, samples, camera, and sensor data; now includes UCO folder. |
| `docs/dataset_strategy.md` | Ready | Staged multi-dataset strategy and no-training boundary are clear. Dataset-specific adapters remain future work. |
| `docs/dataset_selection_table.md` | Ready | Dataset roles and limitations are clear; local schemas still require validation after download. |
| `docs/dataset_pipeline_validation.md` | Ready | Commands, outputs, separation, and limitations match scripts; UCO folder corrected. |
| `docs/uci_dataset_notes.md` | Ready | Correctly separates sensor data from video analysis and warns about label verification. |
| `docs/literature_review.md` | Ready | Safety framing is strong; current squat-only implementation is now distinguished from the six-exercise roadmap. |
| `docs/research_gap.md` | Ready | Avoids diagnostic claims; current MVP versus product roadmap wording was corrected. |
| `docs/references.md` | Partial | Reference list exists; source validity/URL freshness was not independently re-audited during this code-focused review. |
| `docs/custom_dataset_collection_protocol.md` | Ready | Consent, safety, views, labels, metadata, and storage rules are clear. Local metadata is now explicitly Git-ignored. |

## 9. Critical Issues Found

### P0 blocker

- **Environment issue: broken/mixed virtual environment paths.** The pandas import is missing `dateutil.tz`, and the Windows pytest launcher embeds an obsolete external interpreter path. Create a new project-local `.venv`, install `requirements-dev.txt`, and run tests with `python -m pytest`; do not diagnose repository failures from the mixed environment.
- **Required local validation data is absent in this checkout.** Restore licensed UCI/Kaggle data locally and add at least one consented or synthetic squat video. Do not commit these files.

### P1 important

- No real-video end-to-end test has proven upload through JSON response and frontend rendering.
- Backend upload size is unlimited; add a conservative configurable limit during Sprint 2 before non-local use.
- API error and cleanup behavior lacks automated route tests.
- Real UCI schema, metadata inference, and missing-value semantics are not validated against actual files.
- Landmark outputs use only `video_path.stem`; same-named videos from different input folders can overwrite each other's CSV. Address when real camera fixtures are added.

### P2 improvement

- The code folder/workspace spelling `PysioVision-AI` differs from the intended product name `Movena`. No imports or code paths depend on the folder name, so no automatic rename is needed.
- The frontend has two package-manager lockfile styles; standardize on npm or pnpm.
- CORS configuration should become environment-driven before deployment.
- Add frontend tests/linting and expand dataset-service tests.

Safe rename guidance: stop backend/frontend processes, commit or stash all work, rename the parent folder from outside it (for example `Rename-Item -LiteralPath 'PysioVision-AI' -NewName 'Movena'`), reopen the project, recreate or reactivate `.venv` if its scripts contain old absolute paths, and rerun structure/tests/build. A path with spaces is also supported by Python and Node when quoted, but a hyphenated folder is simpler for shell commands.

## 10. Fixes Applied

- Added `data/raw/uco_physical_rehab/` to the dataset validator and raw-content report.
- Added UCO coverage to the dataset structure test and dataset structure documentation.
- Added `data/samples/metadata.csv` to `.gitignore` to reduce accidental participant/consent metadata exposure.
- Corrected literature and research-gap wording so the implemented MVP is squat-only and the six-exercise set is clearly future scope.
- Replaced the broad README Sprint 2 wishlist with a concise Sprint Status, environment checklist, readiness decision, and focused next-sprint link.
- Added this review report and the focused Sprint 2 plan.
- Added explicit `python-dateutil` runtime pinning, root runtime/development requirements files, and Windows-safe `.venv`/`python -m pytest` setup instructions.

No datasets were moved, no model was trained, and no backend/frontend architecture was rewritten.

## 11. Sprint 2 Readiness Decision

**Conditionally Ready after local environment reset and dependency installation**

The repository is structured well enough to begin the focused Squat Analyzer End-to-End MVP sprint. Core calculations and frontend compilation are credible, safety language is present, and missing data paths fail clearly. Sprint 2 must begin with environment repair and a small local test-video fixture set. Sprint 2 cannot be accepted until the full test suite, backend health check, real video upload, JSON response, and frontend rendering pass in the project `.venv`.

## 12. Recommended Sprint 2 Scope

Use the focused **Squat Analyzer End-to-End MVP** plan:

- Establish a reproducible Python environment and green baseline tests.
- Add a privacy-safe local/synthetic squat video fixture and capture guidance.
- Verify MediaPipe landmark extraction and angle creation end to end.
- Harden rep counting and conservative issue flags using synthetic and local fixtures, without training a model.
- Add FastAPI health/upload/error/cleanup integration tests.
- Verify frontend upload, loading, error, and result rendering against the real backend response.
- Add an upload size limit and resolve same-stem landmark output collisions as small hardening tasks.
- Keep database, authentication, deployment, multi-exercise expansion, sensor-camera fusion, and model training out of scope.

## 13. Commands to Run Next

Run from the project root in PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements-dev.txt
python scripts\check_dataset_structure.py
python -m pytest
```

Restore the licensed datasets to their ignored local folders, then run:

```powershell
python scripts\prepare_uci_physical_therapy_dataset.py
python scripts\extract_sensor_features.py
python scripts\prepare_squat_dataset.py
```

After adding at least one local consented or synthetic squat video under `data\samples\` or `data\raw\custom_videos\`:

```powershell
python scripts\extract_landmarks_from_videos.py --max-frames 300
python scripts\create_angle_features.py
```

Start and verify the backend:

```powershell
Set-Location backend
uvicorn app.main:app --reload
Invoke-RestMethod http://localhost:8000/health
```

In a second PowerShell window:

```powershell
Set-Location frontend
npm.cmd install
$env:VITE_API_BASE_URL = "http://localhost:8000"
npm.cmd run build
npm.cmd run dev
```
