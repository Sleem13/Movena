# API Contract

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
- `pose_quality` with detection coverage, critical-landmark visibility, view warning, score, and level;
- `score_breakdown` for depth, knee alignment, trunk control, consistency, and pose confidence;
- a separate 0–1 `analysis_confidence` with level, reasons, and warnings.

`movement_score` describes rule-based movement observations. `analysis_confidence` describes measurement reliability; the two values are not interchangeable. With `include_ml=true`, the experimental prediction adds `ml_confidence_level`, `agrees_with_rule_based`, and `disagreement_note`. ML never overrides rule-based issues, scoring, or feedback.

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

`GET /api/v1/artifacts/reports/{report_id}` downloads the generated PDF. `GET /api/v1/artifacts/overlays/{overlay_id}` downloads or previews the annotated MP4. IDs are opaque UUIDs, files expire after one hour by default, and missing/expired IDs return 404.
