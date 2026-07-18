# Cloud Deployment Preparation

This is a deployment decision record, not a deployment or public-launch authorization.

## Candidate services

| Layer | Options | Gate |
|---|---|---|
| FastAPI backend | Render, Railway, Fly.io, Azure App Service | HTTPS, health checks, restricted CORS, secrets, logs, upload/time limits |
| Web frontend | Vercel, Netlify | Exact API origin and no secret-bearing client variables |
| PostgreSQL | Neon, Supabase, Railway PostgreSQL | TLS, backups, migrations, least privilege, retention review |
| Media/artifacts | S3-compatible storage, Supabase Storage, Cloudinary | Private objects, short-lived signed URLs, deletion/retention controls |

Required backend variables: `APP_ENV`, `APP_VERSION`, `DATABASE_URL`, `CORS_ALLOWED_ORIGINS`, `SECRET_KEY`, `ACCESS_TOKEN_EXPIRE_MINUTES`, `MAX_UPLOAD_SIZE_MB`, `ENABLE_SESSION_HISTORY`, `ENABLE_THERAPIST_DASHBOARD`, `ENABLE_ML_SECOND_OPINION`, `ENABLE_REPORT_GENERATION`, and `ENABLE_OVERLAY_GENERATION`. Mobile uses the public `EXPO_PUBLIC_API_BASE_URL` only.

## Release blockers

- Production must fail configuration review if `SECRET_KEY` is the development default or CORS contains `*`.
- Real patient data is prohibited until privacy, consent, access-control, deletion/retention, breach-response, and regional legal reviews are complete.
- Media requires private object storage; local ephemeral disks and publicly guessable artifact links are insufficient.
- Auth and role enforcement are required for real users. Consent and patient/therapist relationship workflows remain required.
- Structured audit logging, monitoring, backups, rate limiting, malware/media validation, and incident response are recommended before external testing.
- Rule-based analysis remains primary. ML/DL and recognition remain experimental and non-diagnostic.
