# Session History API

## Saving During Analysis

```text
POST /api/v1/analyze/squat?save_session=true
POST /api/v1/analyze/sit-to-stand?save_session=true
```

The normal analysis response gains `session_id`. The default is `save_session=false`, preserving existing behavior. Both successful and rejected analysis responses can be saved.

## Listing

```text
GET /api/v1/sessions?exercise_id=bodyweight_squat&status=success&limit=50&offset=0
```

Returns `items`, `total`, `limit`, and `offset`. Each summary contains exercise, status, time, reps, score, confidence levels, issue codes, and report/overlay links.

## Detail and Delete

```text
GET /api/v1/sessions/{session_id}
DELETE /api/v1/sessions/{session_id}
```

Detail includes JSON snapshots, metrics, and issue rows. Delete removes saved metadata only. Missing IDs return structured `SESSION_NOT_FOUND` errors.

These endpoints have no authentication and are for local development only. They must not be exposed as a production patient-record API.
