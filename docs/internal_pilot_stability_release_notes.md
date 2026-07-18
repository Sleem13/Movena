# Internal Pilot Stability Release Notes

## Candidate

- Candidate ID: `sprint26-stability-001`
- Mobile version: `0.26.0`
- Backend/web version: `0.26.0` when deployed with `APP_VERSION=0.26.0`
- EAS profile: `preview-staging`
- Staging environment: blocked; real private HTTPS URL is not configured
- Android build: blocked; no installable candidate recorded
- iOS: not built or validated
- Distribution: internal only; no public/store release authorized

## Stability changes

- Closed same-tick mobile double-submit race while preserving retry and cancellation.
- Added exercise-specific recording and rejected-result guidance.
- Added friendly artifact-expiry, unsupported-exercise, missing-file, and processing-error messages.
- Kept rejected results not scored and handled zero reps, null breakdowns, and ML not-applicable states.
- Added pilot device metrics and safe partial-row summary handling.
- Added standardized artifact 404 privacy tests.
- Aligned visible web/mobile safety disclaimer wording.

## Supported scope

Only `bodyweight_squat`, `sit_to_stand`, `knee_extension`, `shoulder_abduction`, and `hip_abduction`. Rule-based analyzers remain primary. ML/DL and recognition remain experimental and are not promoted.

## Known remaining issues

No actual pilot feedback exists. Private staging, Android artifact generation, physical-device testing, real network interruption, deployed auth lifecycle, and artifact playback/download remain unvalidated. iOS is not covered. Temporary artifacts can expire by design.

## Automated testing status

- Backend: 189 passed; 7 dependency deprecation warnings.
- Mobile: 58 passed; TypeScript check passed.
- Frontend: 33 passed; production build passed.
- Pilot summary: empty and partial-row regression cases passed; structured CSV import/render verification passed.

These results verify repository behavior only. They do not establish deployed, device, participant, or clinical performance.

## Safety/privacy

Use controlled non-identifying test media only. The app provides movement monitoring, not diagnosis or treatment. No real patient data, raw token, secret, signed URL, or unrestricted debugging media may enter pilot records.

## Decision

**NO-GO for the next internal pilot cycle** until the deployment, install, physical-device, privacy/security, and named-owner gates pass. The codebase is an automated-test-validated stability candidate, not a released pilot build.
