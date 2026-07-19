# Operational Staging Activation Plan

## Decision and current status

Use the existing minimal path: **Render Docker backend + Neon PostgreSQL + Vercel frontend + EAS internal Android**. This matches the checked-in Dockerfile, SQLAlchemy/Psycopg configuration, Vite frontend, and `preview-staging` EAS profile.

Activation is currently **blocked**. No Render, Neon, or Vercel credentials/project identifiers, managed `DATABASE_URL`, staging domains, or active provider resources are available. EAS authentication exists, but its preview environment is empty. Do not invite testers, submit an Android build, or start Sprint 30 until the operational gate checklist passes.

This environment is invite-only product QA. It permits only synthetic or tester-owned non-identifying test media—never real patient data—and it is not for clinical use, diagnosis, or treatment.

## Required access and credentials

| Provider | Required access | Secret handling |
|---|---|---|
| Render | Authorized workspace, linked GitHub repository, web-service administration, service ID, optional deploy-hook URL/API credential | Store only in Render/provider or CI secrets; deploy-hook URLs are secrets |
| Neon | Authorized project/branch administration and a dedicated staging connection string | Store `DATABASE_URL` only in Render/provider secrets |
| Vercel | Authorized team/project access and Git integration or CLI token | Store token outside the repository; `VITE_API_BASE_URL` is public client configuration |
| EAS | Project-owner access to project `3161d775-09da-468e-b97d-f678ca583c4c` | `EXPO_PUBLIC_*` values are public bundle configuration, never secret storage |
| Application | Unique staging admin email/alias and strong password; accountable release, QA, privacy, and safety owners | Store passwords and `SECRET_KEY` only in controlled secret stores |

## Required backend environment

Set these in the Render service. Never populate or commit the example `.env` files.

```text
APP_ENV=staging
APP_VERSION=0.28.0
DATABASE_URL=postgresql+psycopg://<user>:<password>@<host>/<database>?sslmode=require
SECRET_KEY=<unique cryptographically random value of at least 32 characters>
CORS_ALLOWED_ORIGINS=https://<exact-staging-frontend-domain>
REQUIRE_AUTH_FOR_ANALYSIS=true
ENABLE_PUBLIC_DEMO_MODE=false
ACCESS_TOKEN_EXPIRE_MINUTES=60
ARTIFACT_RETENTION_HOURS=24
ENABLE_SESSION_HISTORY=true
ENABLE_THERAPIST_DASHBOARD=true
ENABLE_ML_SECOND_OPINION=false
ENABLE_REPORT_GENERATION=true
ENABLE_OVERLAY_GENERATION=true
```

Wildcard CORS and HTTP origins are prohibited in staging. Do not print `DATABASE_URL`, `SECRET_KEY`, admin passwords, JWTs, or deploy-hook URLs.

## Activation sequence and commands

1. Create a dedicated Neon staging project/branch, require TLS, and copy its pooled connection string into the Render secret `DATABASE_URL`.
2. In Render, create a private-purpose web service from this repository using the root `Dockerfile`. Record the service ID and generated HTTPS origin. Set `/ready` as the health check.
3. In Vercel, create a project rooted at `frontend/`, obtain its stable HTTPS staging origin, then set that exact origin as Render `CORS_ALLOWED_ORIGINS`.
4. Configure Vercel and deploy:

```powershell
npm install --global vercel
cd frontend
vercel link
vercel env add VITE_API_BASE_URL preview
vercel --yes
```

Enter the real Render HTTPS origin when prompted for `VITE_API_BASE_URL`. Do not use localhost or `.example.invalid`.

5. Save the Render environment and deploy from the dashboard, or place the secret deploy-hook URL in the current shell and trigger it without printing it:

```powershell
Invoke-RestMethod -Method Post -Uri $env:RENDER_DEPLOY_HOOK_URL
```

6. Initialize and seed only after the database and service configuration are reviewed; follow `postgresql_activation_checklist.md`.
7. Validate the deployed API:

```powershell
$env:STAGING_BACKEND_URL = "https://<real-render-service-domain>"
Invoke-RestMethod "$env:STAGING_BACKEND_URL/health"
Invoke-RestMethod "$env:STAGING_BACKEND_URL/ready"
Invoke-RestMethod "$env:STAGING_BACKEND_URL/api/v1/exercises"
```

Expected evidence: HTTPS responses, `environment=staging`, correct version, database readiness, five supported exercises, no secret values, exact frontend CORS, and unauthenticated analysis rejected with `401 AUTH_REQUIRED`.

8. Configure EAS only after those endpoint checks pass, then build and install according to `eas_staging_env_setup.md`.

## Rollback

Disable the Render and Vercel deployments, revoke EAS install access, rotate application/database/admin credentials, destroy or reset the Neon staging branch, and delete temporary artifacts. Preserve only privacy-safe operational evidence. Do not preserve user-uploaded videos.

## Current blockers

- No provider credentials, projects, database, domains, or deploy hook are available.
- No deployed endpoint can be tested.
- No active private feedback/support/privacy channels or final sign-off exists.
- No Android build or physical-device evidence exists.

Provider references: [Render Docker deployment](https://render.com/docs/docker), [Render environment variables](https://render.com/docs/configure-environment-variables), [Render deploy hooks](https://render.com/docs/deploy-hooks), [Vercel CLI deployment](https://vercel.com/docs/cli/deploy).
