# Sprint 2 Plan

## Sprint Theme

**Squat Analyzer End-to-End MVP**

## Goal

Deliver and verify one complete, CPU-friendly squat-analysis workflow: a user uploads a squat video, the backend extracts pose landmarks, calculates interpretable angles, counts repetitions, flags a small set of conservative movement issues, returns documented JSON feedback with medical limitations, and the frontend renders the result.

Sprint 2 is a validation and integration sprint. It does not include model training, authentication, database integration, deployment, sensor-camera fusion, or additional exercises.

## Entry Conditions

- Recreate `.venv` from `backend/requirements.txt` and obtain a green baseline `python -m pytest` run.
- Restore licensed datasets locally if dataset scripts are part of validation; keep them Git-ignored.
- Provide at least one privacy-safe consented or synthetic squat video with a known expected rep count.
- Confirm `python scripts/check_dataset_structure.py` and `npm.cmd run build` pass.

## Deliverables

1. Reproducible local backend environment and verified `/health` endpoint.
2. Verified squat upload endpoint from multipart request to `AnalysisResponse` JSON.
3. Local landmark and angle pipeline outputs for approved test video fixtures.
4. Stable rule-based repetition counting for the agreed fixture set.
5. Conservative issue flags for poor depth, trunk lean, possible knee valgus, inconsistent movement, and low pose confidence.
6. Medical disclaimer and limitations in every successful analysis response.
7. Frontend upload, loading, error, and results flow verified against the backend.
8. Automated backend integration tests and focused frontend tests for critical states.
9. Updated README/API notes with tested commands, fixture expectations, and known limitations.

## Tasks

### 1. Environment and baseline

- Create root `.venv` with Python 3.11 and install `backend/requirements.txt`.
- Record installed versions and run `python -m pip check`.
- Run root `python -m pytest` and frontend production build.
- Choose npm or pnpm and retain one lockfile strategy.

### 2. Privacy-safe validation fixtures

- Add instructions for a small local consented or synthetic squat clip; keep video and participant metadata ignored.
- Define expected rep count, camera view, approximate duration, and known limitations for each fixture.
- Include front and side views only if safely available; do not manufacture unsafe movement patterns.

### 3. Camera preprocessing integration

- Run landmark extraction on the approved fixtures and inspect detection coverage.
- Run angle-feature generation and verify expected columns, numeric ranges, timestamps, labels, and metadata.
- Prevent output collisions when two videos share a filename stem.
- Confirm missing MediaPipe, unreadable video, no-pose video, and empty folders produce actionable messages.

### 4. Squat analysis stabilization

- Verify rep state transitions on synthetic sequences and real fixture videos.
- Add minimal temporal smoothing/debouncing only if fixture evidence shows false transitions.
- Validate movement flags with conservative names and camera-view limitations.
- Keep thresholds transparent and rule-based; do not train a model.

### 5. API hardening and tests

- Add tests for `/health`, valid multipart upload, unsupported extension, empty file, unreadable video, no detected pose, response schema, and temporary-file cleanup.
- Add a configurable upload-size limit with a clear 4xx response.
- Ensure unexpected errors are logged without exposing internal paths or stack traces to clients.
- Verify uploaded videos are removed after success and failure.

### 6. Frontend integration

- Verify `VITE_API_BASE_URL` in local development and production build modes.
- Test file selection, disabled submit, loading indicator, backend error detail, retry, and results rendering.
- Confirm every displayed field matches `AnalysisResponse` and missing optional lists render safely.
- Keep the disclaimer visible in the results experience.

### 7. Documentation and evidence

- Update exact PowerShell setup/start/test commands.
- Document the tested fixture conditions, expected outputs, and known failure modes.
- Record test/build results and remaining limitations.
- Keep claims limited to an educational, therapist-support prototype.

## Acceptance Criteria

- `python scripts/check_dataset_structure.py` exits 0 from the project root.
- `python -m pytest` exits 0 in the project `.venv` with no raw dataset dependency.
- `npm.cmd run build` exits 0.
- `GET /health` returns HTTP 200 with `status: "ok"`, project name, and version.
- A supported non-empty squat video returns HTTP 200 and JSON matching `AnalysisResponse`.
- Invalid extension and empty upload return clear HTTP 400 responses.
- Unreadable/no-pose video returns a clear 4xx response and leaves no temporary file.
- A known fixture's rep count matches its agreed expected count or the deviation is documented and accepted.
- Angle fields are finite, bounded to meaningful geometric ranges, and derived only from detected frames.
- Detected issues use conservative wording and include camera/2D limitations.
- Every successful response contains the medical disclaimer and limitations.
- The frontend displays loading, error, score, rep, angle, issue, feedback, summary, and limitation states using the real backend response.
- No raw video, participant metadata, public dataset content, or generated large output is tracked by Git.
- No model training, database, authentication, deployment, multi-exercise implementation, or sensor-camera fusion is added.

## Risks and Mitigations

| Risk | Impact | Mitigation |
|---|---|---|
| MediaPipe/OpenCV installation mismatch on Windows | Backend cannot start or process video | Pin Python 3.11 and the reviewed requirements; rebuild `.venv`; record `pip check`. |
| No approved real video fixture | Cannot validate the end-to-end path | Use a consented local clip or explicitly synthetic/non-identifiable fixture; never commit participant video. |
| Camera view, lighting, or occlusion causes missed landmarks | Unstable angles and rep counts | Add capture guidance, confidence thresholds, and a clear no-pose/low-confidence response. |
| Rule thresholds overstate movement quality | Unsafe or misleading feedback | Use conservative `possible_` wording, expose limitations, and avoid diagnostic/prescriptive claims. |
| Unlimited upload consumes disk/memory/time | Local service instability | Add a configurable size limit, stream uploads, and test cleanup paths. |
| Same-stem videos overwrite processed output | Lost or mislabeled validation data | Derive a collision-safe output name or preserve relative input identity. |
| Frontend/backend schema drift | Broken results page | Treat `AnalysisResponse` as the contract and add route/component contract tests. |
| Scope expansion | MVP remains unverified | Enforce the explicit out-of-scope list and defer enhancements to later sprints. |

## Test Plan

### Unit tests

- Angle calculation: straight, right, degenerate, and representative joint geometry.
- Rep counting: no rep, one rep, multiple reps, incomplete final rep, noisy threshold crossings.
- Issue flags: each issue independently, combinations, and low-confidence input.
- Feedback: known issues, no issues, disclaimer always present.
- Sensor features: dummy windows, missing file, invalid window sizes, missing columns, and no numeric signals.
- Dataset normalization: aliases, missing optional metadata, invalid required coordinates, CSV/JSON input.

### API integration tests

- Health response.
- Valid upload with pose extractor mocked for deterministic JSON.
- Unsupported extension, empty upload, no pose, unreadable video, and internal error mapping.
- Upload-size rejection.
- Temporary-file deletion on every path.

### Pipeline tests

- Empty input folders fail clearly.
- One small local fixture produces landmark CSV with expected schema.
- Landmark CSV produces one angle row per detected frame.
- Two same-stem fixtures do not overwrite each other.
- Generated outputs remain Git-ignored.

### Frontend tests

- API base URL configuration.
- Submit disabled without file.
- Loading and backend error states.
- Complete and partially empty result lists.
- Disclaimer visibility.

### Manual acceptance test

1. Start backend and confirm `/health`.
2. Start frontend with `VITE_API_BASE_URL` set.
3. Upload the agreed squat fixture.
4. Compare rep count and issue flags to fixture expectations.
5. Confirm all result fields, disclaimer, and limitations render.
6. Confirm backend temporary uploads are removed and no raw/generated files appear in `git status`.

## Definition of Done

Sprint 2 is done only when the automated tests, frontend build, health check, one real end-to-end fixture, cleanup verification, safety language, and documentation all pass. A code path that exists but has not processed an approved test video does not count as complete.
