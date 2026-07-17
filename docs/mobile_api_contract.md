# Mobile API contract

Future flow: record a short video, upload it to `POST /api/v1/analyze/{exercise_id}?save_session=true`, display the response, and optionally load `GET /api/v1/sessions`. Future access must be token protected.

Session and therapist calls now require `Authorization: Bearer <access_token>`. A mobile client must use secure platform token storage rather than browser localStorage. Development tokens currently have no refresh flow or server-side logout revocation.

## Squat success

```json
{"session_id":"session-id","exercise":"bodyweight_squat","status":"success","total_reps":3,"movement_score":82,"analysis_confidence":{"level":"moderate"},"feedback":["Keep the full body visible."],"report_download_url":"/api/v1/artifacts/reports/id","overlay_preview_url":"/api/v1/artifacts/overlays/id/preview","overlay_download_url":"/api/v1/artifacts/overlays/id/download"}
```

## Sit-to-stand success

```json
{"session_id":"session-id","exercise":"sit_to_stand","status":"success","total_reps":4,"movement_score":78,"analysis_confidence":{"level":"moderate"},"feedback":["Use a stable camera position."],"ml_prediction":{"enabled":false,"availability":"not_applicable"}}
```

## Invalid movement video

```json
{"exercise":"bodyweight_squat","status":"rejected","error_code":"INVALID_SQUAT_VIDEO","message":"No valid squat movement was detected.","total_reps":0,"movement_score":null,"detected_issues":["no_valid_squat_detected"],"validation_warnings":["Show the full body performing 3–5 repetitions."]}
```

## Upload error

```json
{"status":"error","error_code":"UNSUPPORTED_FILE_TYPE","message":"The upload content type is not a supported video format.","details":[]}
```

Clients must tolerate optional fields, treat relative artifact URLs as relative to the configured API base, and never interpret scores as diagnosis or treatment advice.
