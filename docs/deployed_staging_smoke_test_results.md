# Deployed Staging Smoke-Test Results

Render HTTPS staging and Supabase PostgreSQL are now reachable. The results below record direct checks performed on 2026-07-19; unexecuted auth/upload/artifact and device scenarios remain blocked.

## Gate-closure check — 2026-07-19

- Render backend: `https://name-movena-api-staging.onrender.com`.
- `GET /health`: HTTP 200; version `0.28.0-rc.1`, environment staging, database OK, auth required, public demo disabled.
- `GET /ready`: HTTP 200; database connection OK and artifact directories writable.
- `GET /api/v1/exercises`: HTTP 200; five supported exercises and seven planned/unavailable exercises returned.
- Unauthenticated `POST /api/v1/analyze/squat`: HTTP 401.
- `Origin: https://unapproved.example.com` received no `Access-Control-Allow-Origin` header.
- EAS preview points to the same HTTPS origin and declares app environment staging.
- Secret values were not retrieved, printed, or committed during verification.

Required safe provider values remain `APP_ENV=staging`, a unique non-default `SECRET_KEY` of at least 32 characters, exact `CORS_ALLOWED_ORIGINS=https://<staging-frontend-domain>` with no wildcard, `REQUIRE_AUTH_FOR_ANALYSIS=true`, and `ENABLE_PUBLIC_DEMO_MODE=false`.

| Surface | Check | Status | Evidence/blocker |
|---|---|---|---|
| Backend | Health, ready, exercises | Pass | Direct Render HTTPS checks returned HTTP 200 |
| Backend | Login/auth enforcement | Pass for unauthenticated gate | Unauthenticated squat analysis returned HTTP 401 |
| Backend | Upload validation and five analyzers | Pending | Automated tests pass; physical-device/deployed upload matrix unexecuted |
| Backend | Sessions/therapist dashboard | Partial | Supabase connectivity passes; deployed ownership/lifecycle evidence pending |
| Web | App/library/analyze/results | Blocked | Tests/build pass; no Vercel deployment/API URL |
| Web | Auth/history/artifacts | Blocked | No deployed backend/web |
| Mobile | API/library/guidance | Pending | EAS preview URL configured; post-fix build in progress, no device |
| Mobile | Upload/rejection/token/network | Blocked | 65 automated tests pass; no physical-device execution |
| Security | HTTPS/CORS/secrets/artifacts | Partial | HTTPS/auth and unapproved-origin denial pass; approved-origin, signed artifact, expiry, cleanup checks pending |

Current decision remains **NO-GO**. Basic staging reachability is closed, but Android installation/device QA, active private links, lifecycle checks, and accountable sign-off are still required. This record does not authorize external beta invitations.
