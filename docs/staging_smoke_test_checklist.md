# Staging Smoke-Test Checklist

Record staging build/version, commit, tester, date, device/browser, and evidence. Use only synthetic or non-identifiable media.

## Backend

- [ ] `GET /health` returns staging environment/version and no secret values.
- [ ] `GET /ready` confirms database and writable artifact storage.
- [ ] `POST /api/v1/auth/login` succeeds for the internal staging account and fails cleanly for invalid credentials.
- [ ] `GET /api/v1/exercises` returns five supported analyzers and planned entries as unavailable.
- [ ] `GET /api/v1/exercises/bodyweight_squat` returns supported metadata.
- [ ] Unauthenticated analysis returns `AUTH_REQUIRED`.
- [ ] Unsupported/empty/oversized upload returns the standardized error schema.
- [ ] A non-identifying valid video reaches each of the five supported endpoints.
- [ ] Static/invalid movement is rejected without a score or ML output.
- [ ] Authenticated session save/ownership works when enabled.
- [ ] Report and overlay signed links work before expiry and fail without authorization/signature.
- [ ] `python scripts/cleanup_artifacts.py --dry-run` succeeds; scheduled cleanup is configured.

## Web

- [ ] App and exercise library load over HTTPS without localhost requests.
- [ ] Analyze and result screens handle success, rejection, missing artifacts, and API failure.
- [ ] Login/logout and protected history work when enabled.
- [ ] Disclaimer and stop-for-symptoms guidance remain visible.

## Mobile

- [ ] Internal build reaches the staging API, logs in, and loads exercises.
- [ ] Picker/camera, progress, cancel/retry, rejected results, expired token, and offline handling pass.
- [ ] Signed report/overlay links work without exposing a bearer token.

## Security

- [ ] Exact HTTPS CORS only; staging boot rejects unsafe configuration.
- [ ] Logs contain no secrets, tokens, signed URLs, raw media, or identifying filenames.
- [ ] No artifact is accessible without auth or an unexpired signature.
- [ ] No real patient data, diagnosis claims, or treatment-prescription claims are present.
