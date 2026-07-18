# Sprint 23 — Controlled Cloud Staging Deployment

## Engineering outcome

The repository is prepared for a controlled internal staging deployment: fail-closed staging configuration, Psycopg 3 PostgreSQL support, standardized readiness checks, internal EAS staging profile, explicit client API URLs, expiring signed artifact access, environment templates, and release-gate documentation.

The recommended stack is a single Dockerized FastAPI service on Render/Railway, Vite on Vercel/Netlify, and managed Neon/Supabase PostgreSQL. Local backend artifact storage is permitted for internal single-instance staging only. No cloud service was provisioned and no public release occurred.

## Decision

Sprint 23 is conditionally complete at repository-readiness level. Actual staging deployment, provider secret/database setup, signed Android EAS build, physical-device QA, and deployed smoke/security evidence remain blockers. External pilot is explicitly not approved.

## Local validation record

- Main Python suite: 180 passed; separate backend analyzer/artifact suite: 63 passed.
- Web: 33 tests passed and the Vite production build succeeded with an explicit staging HTTPS API URL.
- Mobile: 42 tests passed, TypeScript passed, Expo dependency/config checks passed.
- Staging simulation: `/health=ok`, `/ready=ready`, SQLite connection and artifact directories healthy, 12 exercises/5 supported, unauthenticated analysis rejected with `401 AUTH_REQUIRED`.
- Cleanup dry-run: passed with no eligible local artifacts.
- `docker compose config`: passed. Image build was not executed because the local Docker daemon was unavailable.
- EAS signed build, provider deployment, and physical-device tests: not executed; credentials/hardware/deployed staging services were unavailable.
