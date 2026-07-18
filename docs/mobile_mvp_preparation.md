# Mobile MVP Preparation

## Sprint 22 hardening

Internal EAS profiles, physical-device instructions, cancellation/retry, double-submit prevention, upload preflight checks, permission-denied recovery, structured error parsing, and invalid/expired-token cleanup are implemented. A selected exercise/video is retained after failure or rejection. Physical Android testing and a signed EAS build remain explicit manual gates; no public release or identifiable patient-data use is approved.

## Sprint 21 implementation status

The first Expo Router/TypeScript shell is implemented in `mobile/`. It includes every screen below, metadata-driven manual selection, existing-video picking, short camera recording, multipart upload progress, success/rejected result handling, SecureStore JWT support, protected history, and safety copy. Backend-side analysis remains the only analysis path.

## Proposed screens

1. Splash and safety-first onboarding
2. Login or clearly bounded demo mode
3. Exercise library
4. Exercise details
5. Camera guidance and visibility checklist
6. Video recording or upload
7. Upload and server-processing progress
8. Result summary with rejection handling
9. Session history
10. Safety, limitations, privacy, and About

## Architecture

The implementation uses React Native with Expo Router as a separate client of the FastAPI service. It uploads a short video to the backend and receives server-side pose and rule-based analysis. It does not perform on-device pose estimation, analysis, diagnosis, or background recording. GPU is not required by the app contract.

Authentication may reuse bearer-token endpoints when enabled, but production mobile storage must use platform secure storage. Refresh, revocation, consent, retention, encrypted storage, and production privacy review remain future gates. Anonymous/demo behavior must follow backend configuration.

## Mobile API needs

- `GET /health`
- `GET /api/v1/exercises`
- `GET /api/v1/exercises/{exercise_id}`
- `POST /api/v1/analyze/squat`
- `POST /api/v1/analyze/sit-to-stand`
- `POST /api/v1/analyze/knee-extension`
- `POST /api/v1/analyze/shoulder-abduction`
- `POST /api/v1/analyze/hip-abduction`
- `GET /api/v1/sessions`
- `GET /api/v1/sessions/{session_id}`

A future client abstraction may expose `POST /api/v1/analyze/{exercise_id}` internally, but the current backend endpoint mapping remains explicit for API stability. The mobile app must read `endpoint_path` from metadata or use the documented map; it must not construct endpoints for planned exercises.

## Client behavior

Clients must tolerate optional fields, resolve artifact URLs against the API base, show upload/processing failures without stack traces, and treat `status=rejected` plus `movement_score=null` as invalid or insufficient movement. ML/recognition labels must remain experimental. Pain or unusual symptoms should prompt stopping and professional review, not an automated clinical conclusion.
