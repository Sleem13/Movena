# Sprint 2 Completion Report

## Final Decision

**Conditionally Complete** — the Squat Analyzer end-to-end MVP works locally across the custom-video data pipeline, live backend upload endpoint, and production frontend build. Sprint 3 may start with the limitations below carried into its backlog. The only dataset-closure condition is missing `squat_fast_uncontrolled` coverage; this does not block the verified correct-squat MVP path.

## Data Pipeline Results

Validated on July 11, 2026 using the project-local virtual environment:

- Dataset structure check: passed.
- Supported custom videos detected: 17.
- Supplied pre-curation baseline: 64,119 landmark rows and 1,943 frame-level angle rows.
- Final post-curation rerun: 64,152 landmark rows across all 17 videos and 1,944 frame-level angle rows.
- Landmark extraction failures: 0.
- Unsupported files in the custom-video tree: 0.
- Label counts: 9 correct, 2 shallow depth, 1 knee valgus, 4 trunk lean, 0 fast/uncontrolled, and 1 review-only unlabeled video.

The misleading `squat_correct_002.mp4` file in `squat_trunk_lean` was renamed to `squat_trunk_lean_004.mp4`, applying its curated parent-folder label. `squat_unlabeled` remains a quarantine/review bucket. It is discoverable for pose-pipeline QA but is not an official supervised label and must not be used for labeled training or accuracy claims until manually curated.

## Automated Verification

- `python -m pytest`: **22 passed**.
- `npm run build`: passed; Vite transformed 1,632 modules and generated the production bundle.

## Backend Status

The backend started successfully with:

```powershell
Set-Location backend
python -m uvicorn app.main:app --reload
```

Live HTTP results:

| Check | Result |
|---|---|
| `GET /health` | `200`, JSON status `ok` |
| Real `squat_correct_001.mp4` upload | `200`, valid `AnalysisResponse` JSON |
| Missing multipart `video` field | `422`, structured validation JSON |
| Unsupported `.md` upload | `400`, allowed extensions listed |
| Empty `.mp4` upload | `400`, `Uploaded video is empty.` |
| Unreadable/broken `.mp4` upload | `422`, `Unable to open uploaded video.` |

The real-video response reported 112 pose-detected frames, 1 repetition, average knee/hip/trunk angles of 100.32/74.63/49.02 degrees, a movement score of 60, conservative issue flags, corrective feedback, and three limitations including the clinical disclaimer. It contained every required field: `exercise`, `status`, `total_reps`, the three averages, `movement_score`, `detected_issues`, `feedback`, and `limitations`.

## Frontend Status

**Build verified; implementation reviewed.** The React frontend contains:

- a video upload page with supported MIME filtering and disabled submit before selection;
- an analyzing/loading state and spinner;
- result cards for repetitions, angles, and movement score;
- detected issues, feedback, and known limitations display;
- backend-detail and fallback error display;
- `VITE_API_BASE_URL`, defaulting to `http://localhost:8000`.

The production build passed. A complete manual rendered-browser upload was not completed during closure because the local browser-control session did not return usable page state; therefore frontend status is based on build evidence and focused source review, not a claimed manual UI acceptance test.

## Issues Found and Fixes Applied

- Fixed the misleading filename in the trunk-lean folder by renaming it to `squat_trunk_lean_004.mp4`.
- Made the unlabeled-folder metadata warning explicitly mark videos as review-only and excluded from supervised-label use.
- Refreshed generated metadata, landmarks, angle features, and the validation report after curation.
- Updated the README with Sprint 2 status and exact pipeline/backend/frontend commands.

No backend API, architecture, trained model, or major feature was added.

## Known Limitations

- No `squat_fast_uncontrolled` video is available, so that label has no empirical coverage.
- One video remains unlabeled and quarantined from supervised-label use.
- Dataset size and subject/viewpoint diversity are too small for clinical-performance or generalization claims.
- Rep counting and issue detection are transparent heuristics over 2D MediaPipe landmarks, not clinically validated measurements.
- Camera angle, lighting, occlusion, clothing, and incomplete body visibility can materially change results.
- MediaPipe tracking can vary slightly between runs: the final rerun detected one additional pose frame in the review-only unlabeled clip, changing totals by 33 landmark rows and one angle row without changing video-level success.
- The valid fixture returned `possible_knee_valgus` and `excessive_trunk_lean` despite residing in the correct folder; this highlights that folder labels and rule thresholds require expert review rather than being treated as ground truth.
- Frontend automated component tests are not present, and a full manual rendered-browser acceptance pass remains desirable.
- There is no configurable upload-size limit yet; this should be addressed before exposing the service outside trusted local development.

## Sprint 3 Readiness

Sprint 3 can start, provided it treats this system as an educational local prototype. Priorities should be expert review of rule thresholds and curated labels, collection of fast/uncontrolled and more diverse consented fixtures, frontend component/integration tests, and an upload-size guard before any wider deployment work.
