# Product API Design

This document describes future contracts. It does not implement identity, authorization, persistence, therapist access, or new exercise analyzers.

## Current Active APIs

- `POST /api/v1/analyze/squat`
- `GET /api/v1/artifacts/reports/{report_id}`
- `GET /api/v1/artifacts/overlays/{overlay_id}/preview`
- `GET /api/v1/artifacts/overlays/{overlay_id}/download`

The current squat API remains supported throughout the planned migration.

## Design Principles

- `/api/v1` remains backward compatible.
- Opaque UUIDs replace sequential identifiers.
- Responses distinguish processing state, input validity, measurement confidence, and movement observations.
- Authorization is resource- and tenant-scoped; a user ID in a URL never grants access by itself.
- Uploads are temporary unless the user explicitly consents to retention.
- Idempotency keys protect session creation and retried uploads.

## Exercise Catalog and Analysis

### `GET /api/v1/exercises`

Returns active and planned exercises with ID, display name, status, supported views, recording guide, analyzer version, and limitations. Planned entries cannot be analyzed.

### `GET /api/v1/exercises/{exercise_id}`

Returns detailed instructions and availability. Unknown IDs return `EXERCISE_NOT_FOUND`; inactive IDs return `EXERCISE_NOT_AVAILABLE`.

### `POST /api/v1/analyze/{exercise_id}`

Accepts a temporary video and existing analysis options. It resolves the analyzer through the exercise registry and returns a consistent envelope with exercise-specific metrics. `/api/v1/analyze/squat` remains an alias during migration.

## Sessions

### `POST /api/v1/sessions`

Creates an analysis-session record from an authorized exercise assignment or standalone monitoring flow. Suggested fields: exercise ID, client-generated idempotency key, capture metadata, consent/retention choice, optional patient-reported context, and upload reference. Returns opaque session ID and processing state.

### `GET /api/v1/sessions/{session_id}`

Returns state (`created`, `uploading`, `processing`, `completed`, `rejected`, `failed`, `expired`), analysis summary, artifact links, versions, and limitations for an authorized caller.

### `GET /api/v1/users/{user_id}/sessions`

Returns a cursor-paginated, access-controlled session summary. Future clients should prefer `/me/sessions` for self-service to reduce identifier misuse.

## Therapist APIs

- `GET /api/v1/therapist/patients`: paginated authorized caseload, not a directory search.
- `GET /api/v1/therapist/patients/{patient_id}/sessions`: authorized review history with consent scope.
- `POST /api/v1/therapist/patients/{patient_id}/exercise-plan`: records therapist-entered assignments; AI does not prescribe.

These endpoints require future authentication, clinic tenancy, role/relationship authorization, audit logging, and revocation. They must not be implemented as unauthenticated placeholders.

## Artifact APIs

- `GET /api/v1/artifacts/reports/{report_id}`
- `GET /api/v1/artifacts/overlays/{overlay_id}/preview`
- `GET /api/v1/artifacts/overlays/{overlay_id}/download`

Current temporary artifact behavior remains. Persistent sessions will require signed short-lived access, authorization, retention metadata, safe content disposition, range-request support for video, and deletion propagation.

## Common Error Envelope

```json
{
  "status": "error",
  "error_code": "EXERCISE_NOT_AVAILABLE",
  "message": "This exercise is not available for analysis.",
  "details": [],
  "request_id": "opaque-id"
}
```

No error exposes stack traces, filesystem paths, model internals, patient existence, or authorization details.

## Versioning

API version, analyzer version, threshold version, pose-backend version, report version, and optional ML version are separate. A session records each one so historical results remain interpretable after upgrades.
# Therapist Prototype API

Sprint 11 adds unauthenticated local-development routes under `/api/v1/therapist` for placeholder profiles, session assignment, progress aggregation, and dashboard summaries. Unknown `patient_id` values during analysis produce an unassigned saved session plus warning. Production exposure is blocked on authentication, role-based authorization, consent, auditing, and privacy review.
# Deployment and mobile contract note

Clients configure one API base URL and may use `GET /health`, `GET /ready`, analysis, artifact, session, and therapist routes. Errors follow `{status, error_code, message, details}`. Mobile clients should upload multipart video, accept optional response fields, and resolve relative artifact URLs against the API base. Future access to history and therapist resources requires token-based authorization.

Sprint 13 adds `/api/v1/auth/register`, `/login`, `/me`, and `/logout`. Session routes require authentication; therapist routes require therapist/admin. Analysis is configurable through `REQUIRE_AUTH_FOR_ANALYSIS`, while authenticated session saves record ownership. Auth failures use `AUTH_REQUIRED`, `INVALID_TOKEN`, `TOKEN_EXPIRED`, `INSUFFICIENT_ROLE`, or `USER_INACTIVE`.
