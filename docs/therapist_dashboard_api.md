# Therapist Dashboard Prototype API

All routes are unauthenticated local-development endpoints under `/api/v1/therapist`:

- `GET /dashboard`
- `GET|POST /patients`
- `GET|PATCH|DELETE /patients/{patient_id}`
- `GET /patients/{patient_id}/sessions`
- `POST /patients/{patient_id}/sessions/{session_id}`
- `GET /patients/{patient_id}/progress`

Progress includes session totals by exercise, average available score/confidence, latest date, issue counts, and low-confidence count. Missing numeric evidence remains null rather than being inferred.

Analysis can assign a saved session with `save_session=true&patient_id=...`. An unknown profile does not discard the analysis or session; it saves the session unassigned and returns a warning. This API must not be exposed publicly without authentication and authorization.
