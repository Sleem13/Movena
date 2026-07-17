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

## Experimental recognition endpoints

- `GET /api/v1/recognition/models` lists optional experimental artifacts and supported tracks.
- `POST /api/v1/recognition/exercise` currently accepts precomputed feature JSON only.

Mobile clients must not auto-route from recognition. They may show a suggestion only with its experimental warning and a confirmation step. `analyzer_available=false` means the exercise is planned or unsupported and must not produce feedback. Upload-to-recognition extraction is not enabled in this foundation.

## Knee-extension endpoint

Use `POST /api/v1/analyze/knee-extension`. Manual selection remains primary, and ML is explicitly not applicable.

```json
{"session_id":"session-id","exercise":"knee_extension","exercise_id":"knee_extension","exercise_name":"Knee Extension","status":"success","total_reps":3,"valid_reps":3,"movement_score":84,"analysis_confidence":{"level":"medium"},"ml_prediction":{"enabled":false,"model_version":"not_applicable"}}
```

## Shoulder-abduction endpoint

Use `POST /api/v1/analyze/shoulder-abduction`. Manual selection remains primary, and ML is explicitly not applicable.

```json
{"exercise":"shoulder_abduction","exercise_id":"shoulder_abduction","exercise_name":"Shoulder Abduction","status":"success","total_reps":3,"valid_reps":3,"average_shoulder_angle":86,"movement_score":84,"analysis_confidence":{"level":"medium"},"ml_prediction":{"enabled":false,"model_version":"not_applicable"}}
```

## Hip-abduction endpoint

Use `POST /api/v1/analyze/hip-abduction`. The standing front-view variant is the MVP, manual selection remains primary, and ML is explicitly not applicable.

```json
{"exercise":"hip_abduction","exercise_id":"hip_abduction","exercise_name":"Hip Abduction","status":"success","total_reps":3,"valid_reps":3,"average_hip_abduction_angle":30,"movement_score":84,"analysis_confidence":{"level":"medium"},"ml_prediction":{"enabled":false,"model_version":"not_applicable"}}
```
