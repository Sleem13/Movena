# Staging Secrets Configuration

Configure these in Render: `APP_ENV=staging`, `APP_VERSION=0.28.0`, `DATABASE_URL`, `SECRET_KEY`, `CORS_ALLOWED_ORIGINS`, `ACCESS_TOKEN_EXPIRE_MINUTES=60`, `MAX_UPLOAD_SIZE_MB=100`, `ALLOWED_VIDEO_EXTENSIONS`, `ARTIFACT_RETENTION_HOURS=24`, feature flags, `ENABLE_ML_SECOND_OPINION=false`, `ENABLE_PUBLIC_DEMO_MODE=false`, and `REQUIRE_AUTH_FOR_ANALYSIS=true`.

Vercel needs public `VITE_API_BASE_URL`. EAS preview needs public `EXPO_PUBLIC_API_BASE_URL` and the profile supplies `EXPO_PUBLIC_APP_ENV=staging`. Public client variables are not secret storage.

Generate the backend secret with a cryptographically secure provider tool and store it only in the provider. Staging startup rejects default/short secrets, wildcard/non-HTTPS CORS, public demo mode, and unauthenticated analysis.

Verify without revealing values:

- Confirm required variable names are present in the provider dashboard.
- Check `/health` reports `environment=staging`, `app_version=0.28.0`, and expected feature booleans.
- Check an unauthenticated analysis returns `401 AUTH_REQUIRED`.
- Never echo `DATABASE_URL`, `SECRET_KEY`, admin password, JWT, or signed artifact URL.

Rotate immediately after suspected exposure, staff/access changes, and on the documented periodic schedule. Rotation requires invalidating existing JWTs/signed links, updating the provider secret and database credential, redeploying, testing auth/readiness, and revoking the old values.

## Pytest environment isolation

Repository tests set `APP_ENV=test` and test-only values in `tests/conftest.py` before importing `app.main`. This makes `python -m pytest` deterministic even when the invoking shell contains staging variables. Test and development environments may use localhost HTTP CORS origins; staging and production still require an explicit non-default secret, HTTPS-only CORS origins, authenticated analysis, and disabled public demo mode.

The pytest secret and SQLite database URL are local test fixtures only. They must never be copied into a deployed environment. Application logs and test output must not print secret values or database credentials.

Avoid intentionally running local tests as staging or reusing test values in a staging shell. For phone or LAN testing over HTTP, use `APP_ENV=development`; use `APP_ENV=staging` only with real HTTPS API and frontend origins.
