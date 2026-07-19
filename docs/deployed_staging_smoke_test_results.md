# Deployed Staging Smoke-Test Results

No provider staging environment exists, so deployed rows are blocked rather than reported as passes.

## Gate-closure attempt — 2026-07-19

- Intended providers remain Render (backend), Neon (PostgreSQL), and Vercel (frontend).
- `RENDER_API_KEY`, `NEON_API_KEY`, and `VERCEL_TOKEN` are unset; the corresponding provider CLIs are not installed, and no provider project identifiers or deployed URLs are configured in the workspace.
- `DATABASE_URL`, `SECRET_KEY`, `CORS_ALLOWED_ORIGINS`, and staging client API URLs are unset. Checked-in `.env.staging.example` files contain only empty values or `.example.invalid` placeholders.
- Therefore no backend or frontend was deployed and no secret was generated, displayed, or committed.
- `GET /health`, `GET /ready`, and `GET /api/v1/exercises` could not be exercised against HTTPS staging because no staging origin exists. Local automated coverage is not substituted for deployed evidence.

Required safe provider values remain `APP_ENV=staging`, a unique non-default `SECRET_KEY` of at least 32 characters, exact `CORS_ALLOWED_ORIGINS=https://<staging-frontend-domain>` with no wildcard, `REQUIRE_AUTH_FOR_ANALYSIS=true`, and `ENABLE_PUBLIC_DEMO_MODE=false`.

| Surface | Check | Status | Evidence/blocker |
|---|---|---|---|
| Backend | Health, ready, exercises | Blocked | Local staging rehearsal passed; no Render URL |
| Backend | Login/auth enforcement | Blocked | Local `401 AUTH_REQUIRED` passed; no seeded Neon account |
| Backend | Upload validation and five analyzers | Blocked | Automated/local API tests pass; no deployed service |
| Backend | Sessions/therapist dashboard | Blocked | Automated ownership/API tests pass; no deployed PostgreSQL |
| Web | App/library/analyze/results | Blocked | Tests/build pass; no Vercel deployment/API URL |
| Web | Auth/history/artifacts | Blocked | No deployed backend/web |
| Mobile | API/library/guidance | Blocked | EAS preview API variable absent |
| Mobile | Upload/rejection/token/network | Blocked | Automated tests pass; no internal APK/device |
| Security | HTTPS/CORS/secrets/artifacts | Blocked | Fail-closed code tests pass; provider values unavailable |

This document must be updated with timestamped URLs, versions, tester, sanitized evidence, and pass/fail results after deployment. Current decision: **blocked / NO-GO**. It does not authorize internal or external beta invitations.
