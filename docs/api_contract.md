# API Contract

## Rehabilitation Phase 1 additions

- `GET /api/v1/patient/today` returns scheduled plan dosage, recorded completion/pain/difficulty/fatigue/comment values, optional analysis linkage, the next appointment, unread notifications, and 7-day completion summaries.
- `POST /api/v1/patient/adherence` idempotently creates or updates a daily check-in. `analysis_session_id` is optional; when supplied, the server verifies patient ownership and exercise identity before linking it to the assigned plan item.
- `GET /api/v1/therapist/patients/{patient_id}/adherence` is assignment-protected and returns subjective outcomes separately from the optional AI session reference.
- `POST /api/v1/therapist/patients/{patient_id}/exercise-plans` creates a new plan version and pauses the prior active version instead of overwriting history. Plan items support rest interval, tempo, schedule days, targets, video request, and AI-analysis requirement.

AI results are movement-analysis data only. They do not alter treatment or replace clinician review.

## `GET /health`

Returns `200` JSON with `status`, `project`, and `version`.

## `POST /api/v1/analyze/squat`

Send `multipart/form-data` with one `video` file. Supported extensions are MP4, MOV, AVI, MKV, and WEBM. Declared MIME type must be a corresponding video type or `application/octet-stream`. Maximum upload size is 100 MB. Uploaded files are stored under a generated name only while processing and deleted after success or failure.

Successful `200` responses contain:

- `exercise`, `status`, and `total_reps`;
- `average_knee_angle`, `average_hip_angle`, and `average_trunk_angle` in degrees;
- a 0–100 educational `movement_score`;
- `detected_issues`, patient-facing `feedback`, `summary`, and `limitations`.

Errors use this stable envelope:

```json
{
  "status": "error",
  "error_code": "INVALID_FILE_TYPE",
  "message": "Only supported video files are accepted.",
  "details": []
}
```

Current codes are `MISSING_FILE`, `INVALID_FILE_TYPE`, `FILE_TOO_LARGE`, `EMPTY_FILE`, `VIDEO_OPEN_FAILED`, `NO_POSE_DETECTED`, and `PROCESSING_ERROR`. Low landmark confidence is returned as a successful report issue because a cautious result can still be useful; it is not treated as transport failure.

This API uses rule-based 2D pose analysis. It is sensitive to viewpoint, visibility, lighting, and movement context. It does not diagnose injury or replace assessment by a licensed physiotherapist.

### Accuracy and confidence fields

Successful responses also include:

- `rep_events`, `rep_durations`, `ignored_partial_reps`, and a 0–1 `rep_count_confidence`;
- optional `partial_rep_events` with start/end frames and an aggregated failure reason;
- `pose_quality` with detection coverage, critical-landmark visibility, view warning, score, and level;
- `score_breakdown` for depth, knee alignment, trunk control, consistency, and pose confidence;
- a separate 0–1 `analysis_confidence` with level, reasons, and warnings.

`movement_score` describes rule-based movement observations. `analysis_confidence` describes measurement reliability; the two values are not interchangeable. With `include_ml=true`, the experimental prediction adds `ml_confidence_level`, `agrees_with_rule_based`, and `disagreement_note`. ML never overrides rule-based issues, scoring, or feedback.

`ignored_partial_reps` counts aggregated meaningful incomplete intervals, not every noisy threshold transition. If rep confidence is below 0.50, a valid response remains successful but includes a manual-review warning in `analysis_confidence.warnings`.

### Invalid squat recordings

Before scoring or optional ML inference, the endpoint checks pose-frame count, active-segment pose coverage, whole-video pose coverage, critical-landmark visibility, knee and hip angle ranges, temporal motion variation, and completed squat repetitions. Static/profile-image videos, incomplete-body recordings, and zero-rep recordings return HTTP 200 with `status: "rejected"`, `error_code: "INVALID_SQUAT_VIDEO"`, and `movement_score: null`. They do not receive `poor_depth` as a substitute for a valid attempt.

```json
{
  "exercise": "bodyweight_squat",
  "status": "rejected",
  "error_code": "INVALID_SQUAT_VIDEO",
  "message": "No valid squat movement was detected.",
  "total_reps": 0,
  "movement_score": null,
  "detected_issues": ["no_valid_squat_detected"],
  "input_validity": {
    "is_valid": false,
    "reason": "no_valid_squat_detected",
    "valid_reps": 0,
    "warnings": ["No complete squat repetition was detected."]
  }
}
```

If `include_ml=true`, the response contains a disabled ML result with the warning `ML prediction skipped because no valid squat movement was detected.` No model prediction is performed. Reports and overlays are also skipped for rejected inputs.

### Sprint 4 query options and artifacts

- Default: summary JSON only; frame and artifact fields are null.
- `generate_report=true`: creates a temporary PDF and returns `report_id` and `report_download_url`.
- `include_frame_data=true`: includes at most 300 sampled detected-pose frame rows with timestamp, angles, phase, and an optional possible issue.
- `include_overlay=true`: generates an experimental annotated MP4 and returns `overlay_id` and `overlay_download_url`.

`GET /api/v1/artifacts/reports/{report_id}` downloads the generated PDF. `GET /api/v1/artifacts/overlays/{overlay_id}` downloads or previews the annotated MP4. IDs are opaque UUIDs, files follow `ARTIFACT_RETENTION_HOURS` (24 hours by default), and missing/expired IDs return 404.
# Sit-to-Stand Analysis (Sprint 9)

`POST /api/v1/analyze/sit-to-stand` accepts the same multipart `video` upload and optional `include_overlay`, `include_frame_data`, and `generate_report` flags as the squat endpoint. `include_ml` is accepted for client compatibility but returns a disabled result because no sit-to-stand model exists.

Successful responses use `exercise: "sit_to_stand"` and include rep events with `start_frame`, `standing_frame`, `end_frame`, duration, and knee-angle extrema. Invalid or zero-repetition recordings return `status: "rejected"`, `error_code: "INVALID_SIT_TO_STAND_VIDEO"`, and `movement_score: null`.

The existing `POST /api/v1/analyze/squat` contract is unchanged. Both endpoints provide educational, non-diagnostic output.

# Saved Session Metadata (Sprint 10)

Both analysis endpoints accept `save_session=false` by default. When true, the response includes a UUID `session_id`; a persistence failure does not replace the analysis and instead appends `Session could not be saved.` to validation warnings.

`GET /api/v1/sessions` lists summaries with optional `exercise_id`, `status`, `limit`, and `offset`. `GET /api/v1/sessions/{session_id}` returns detail, and `DELETE /api/v1/sessions/{session_id}` removes metadata only. These unauthenticated endpoints are restricted to local development and are not a clinical record system.
