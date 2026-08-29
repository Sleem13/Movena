# Care Platform Implementation and Launch Gate

Updated: 2026-08-28

## Implemented baseline

The repository now contains a migration-managed PostgreSQL care-platform baseline alongside the existing movement-analysis APIs. SQLite remains available only for local development and deterministic tests; production startup requires PostgreSQL and verifies that Alembic revision `0003_data_rights` is installed.

Implemented server capabilities include:

- patient, therapist, admin, super-admin, support, and research-demo roles;
- patient-owned profiles, explicit therapist assignments, and scoped patient access;
- health profiles, versioned consents, scheduled exercise plans, adherence/pain/difficulty entries, configurable safety alerts, and audit events;
- therapist availability, UTC appointments, transactional conflict checks, Cairo display time, cancellation rules, attendance state, clinical notes, and reminders;
- private Daily rooms and short-lived participant tokens with a -15/+30 minute join window and recording disabled;
- EGP services and packages, server-created Paymob checkout, verified/idempotent webhooks, appointment activation after webhook confirmation, and audited full/partial refunds;
- patient and therapist reports, private artifact authorization, notification preferences and retry processing, catalog/admin metrics, and auditable data-rights requests;
- Arabic/English responsive patient Web UI and Expo screens for today, appointments/video join, notifications, and billing;
- an experimental feature flag boundary around live AI coaching. It is not part of the clinical care path.

Run schema deployment from the repository root:

```powershell
alembic upgrade head
alembic current
```

Run the notification/reminder worker on a recurring scheduler:

```powershell
.\.venv\Scripts\python.exe scripts\process_notifications.py
```

## Required production configuration

Use a Supabase PostgreSQL connection string as `DATABASE_URL`, with TLS enabled and connection pooling configured for the deployment runtime. Apply Alembic with a migration owner before starting the API. The application account must not be the database owner and must not bypass RLS. The baseline migration denies direct `anon` and `authenticated` table access because the current architecture uses the FastAPI service as the only data-access boundary.

Store these values only in the deployment secret manager:

- `SECRET_KEY`
- `DATABASE_URL`
- `DAILY_API_KEY`, `DAILY_DOMAIN`, and `ENABLE_TELEMEDICINE=true`
- `PAYMOB_API_KEY`, `PAYMOB_INTEGRATION_ID`, `PAYMOB_IFRAME_ID`, `PAYMOB_HMAC_SECRET`, and `ENABLE_PAYMENTS=true`
- SMTP credentials when email delivery is enabled

Production must use exact HTTPS origins in `CORS_ALLOWED_ORIGINS`, authenticated analysis, disabled public demo mode, and the notification worker. Never place any of the server values above in `VITE_*` or `EXPO_PUBLIC_*` variables.

## Evidence captured locally

- Backend: `296 passed` (the existing 293 plus three care-platform security tests).
- Web: `114 passed`; Vite production build completed.
- Mobile: `95 passed`; TypeScript check completed.
- Browser QA: patient registration/login, consent capture, care dashboard, adherence dialog, English/Arabic RTL, and a 390x844 viewport were exercised locally.

This evidence supports local implementation readiness only. It is not production, legal, medical, provider, or physical-device approval.

## Hard launch blockers

The public launch decision remains **NO-GO** until all items below have named owners and retained evidence:

- Daily sandbox and production calls tested with real credentials, including expired/unauthorized tokens, provider failure, and weak network behavior;
- Paymob card and wallet sandbox matrices completed, including success, failure, cancel, forged/duplicate webhook, browser-return loss, and refund reconciliation;
- email retry worker and duplicate prevention verified through the production email provider;
- WAF/gateway rate limiting and managed protections enabled at the public edge;
- private media upload for doctor-requested follow-up videos completed with malware/content inspection, type/size limits, signed access, retention, and deletion;
- data export, correction, deletion, and account-erasure operational procedures completed and restore-safe deletion verified; the current API records and audits requests but does not autonomously erase clinical records;
- backup/restore test, incident drill, monitoring alerts, performance/load test, and vulnerability scan completed;
- Chrome, Edge, Safari, Android, and iPhone physical-device tests completed, including cameras, deep links, payment, Daily calls, and weak networks;
- accessibility review and the 18 acceptance criteria from the requirements document signed off by patients and therapists;
- an independent Egyptian legal/privacy review and named clinical safety approval completed before identifiable patient data is entered.

The Expo appointment screen currently launches the protected Daily meeting URL through the device browser. Embedding a native Daily React Native call surface is a post-baseline item and must be completed if an in-app call is a launch requirement.

## Release decision

Do not enable `ENABLE_TELEMEDICINE`, `ENABLE_PAYMENTS`, real-patient onboarding, or the Live AI Coaching flag in production merely because local tests pass. Promotion requires the full gate above, including legal and clinical sign-off. The movement-analysis output remains assistive and must not diagnose or prescribe treatment.
