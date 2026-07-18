# Deployed Staging Smoke-Test Results

No provider staging environment exists, so deployed rows are blocked rather than reported as passes.

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

This document must be updated with timestamped URLs, versions, tester, sanitized evidence, and pass/fail results after deployment. It does not authorize an internal pilot yet.
