# Therapist Dashboard Prototype API

All routes are local-development prototype endpoints under `/api/v1/therapist`
and require an authenticated `therapist` or `admin` role:

- `GET /dashboard`
- `GET|POST /patients`
- `GET|PATCH|DELETE /patients/{patient_id}`
- `GET /patients/{patient_id}/sessions`
- `POST /patients/{patient_id}/sessions/{session_id}`
- `GET /patients/{patient_id}/progress`

Progress includes session totals by exercise, average available score/confidence,
source-value counts, latest date, issue counts, low-confidence count, and
explicit metric provenance. Missing numeric evidence remains null rather than
being inferred.

Analysis can assign a saved session with `save_session=true&patient_id=...`. An unknown profile does not discard the analysis or session; it saves the session unassigned and returns a warning. This API must not be exposed publicly without authentication and authorization.
