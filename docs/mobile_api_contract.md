# Mobile API contract

## Sprint 24 internal-build gate

An internal staging build must receive the real HTTPS API URL from EAS preview variables. Building against localhost, `10.0.2.2`, or an `.invalid` placeholder is prohibited. The current build is blocked until a deployed API exists; mobile behavior remains covered by automated tests only.

## Staging contract

Staging uses `EXPO_PUBLIC_API_BASE_URL=https://<staging-backend>` from the EAS preview environment and requires authentication for analysis. Artifact URLs may include short-lived `expires` and `signature` query parameters; clients must preserve the complete URL, must not log it, and must treat expiry as a request to re-run or refresh the authorized analysis rather than append a bearer token to the URL.

## Sprint 22 client reliability behavior

The mobile client maps `FILE_TOO_LARGE`, `UNSUPPORTED_FILE_TYPE`, `EMPTY_FILE`, `INVALID_FILENAME`, `AUTH_REQUIRED`, `INVALID_TOKEN`, `TOKEN_EXPIRED`, `INSUFFICIENT_ROLE`, `INVALID_*_VIDEO`, `NETWORK_ERROR`, `TIMEOUT`, and `SERVER_UNAVAILABLE` to non-technical messages. Rejected analysis is a result state, not a transport crash. `401`, `INVALID_TOKEN`, and `TOKEN_EXPIRED` clear the SecureStore token and request login. Upload cancel/retry retains the manually selected exercise and file; no token, raw media, or patient identifier may enter logs.

Missing movement score, score breakdown, confidence, pose quality, artifacts, or ML output must remain missing/unavailable. Clients never synthesize a score. Native LAN testing uses `http://<LAN_IP>:8010`; Android emulator may use `http://10.0.2.2:8010`.

Future flow: record a short video, upload it to `POST /api/v1/analyze/{exercise_id}?save_session=true`, display the response, and optionally load `GET /api/v1/sessions`. Future access must be token protected.

Session and therapist calls now require `Authorization: Bearer <access_token>`. A mobile client must use secure platform token storage rather than browser localStorage. Development tokens currently have no refresh flow or server-side logout revocation.

The current concrete endpoint map is:

| Exercise ID | Endpoint |
|---|---|
| `bodyweight_squat` | `POST /api/v1/analyze/squat` |
| `sit_to_stand` | `POST /api/v1/analyze/sit-to-stand` |
| `knee_extension` | `POST /api/v1/analyze/knee-extension` |
| `shoulder_abduction` | `POST /api/v1/analyze/shoulder-abduction` |
| `hip_abduction` | `POST /api/v1/analyze/hip-abduction` |

Use `GET /api/v1/exercises` to discover supported and planned exercises. Only records with `supported_in_app=true` and a non-null `endpoint_path` may be selected.

## Sprint 21 mobile request behavior

The Expo app reads `EXPO_PUBLIC_API_BASE_URL`; Android emulators commonly use `http://10.0.2.2:8010`, while physical devices use the backend computer's LAN IP. Analysis requests send `multipart/form-data` with the field name `video`. Query parameters include `save_session`, `include_overlay`, `generate_report`, `include_ml=false`, and `include_frame_data=false`. `patient_id` is sent only when explicitly provided by a supported workflow.

Bearer tokens are read from Expo SecureStore and added as `Authorization: Bearer <token>`. No production secret is bundled in the app. Mobile clients must handle timeouts, offline/backend-unreachable states, structured upload errors, invalid movement rejections, and expired tokens.

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

## Unsupported planned exercise

Planned exercises do not have analyzer routes and clients should prevent submission. An unknown metadata lookup returns:

```json
{"status":"error","error_code":"EXERCISE_NOT_FOUND","message":"Exercise metadata was not found.","details":["Use GET /api/v1/exercises to view supported and planned exercises."]}
```

## Authentication required

When authentication is enabled for a protected operation:

```json
{"status":"error","error_code":"AUTHENTICATION_REQUIRED","message":"Authentication is required.","details":[]}
```

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
