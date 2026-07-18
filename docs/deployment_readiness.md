# Deployment Readiness

## Sprint 24 execution gate

The provider path, secrets procedure, staging Compose rehearsal, PostgreSQL setup, internal-build report, smoke matrix, artifact review, and pilot package are complete. Actual Render/Neon/Vercel provisioning, EAS Android build, and physical-device QA are blocked by missing deployment configuration/API URL/device evidence. Deployment readiness does not equal pilot approval.

## Sprint 23 controlled staging boundary

Repository readiness now includes fail-closed staging settings, PostgreSQL/Psycopg support, explicit web/mobile API origins, signed temporary artifacts, and staging checklists. Provider deployment, HTTPS/database setup, scheduled cleanup, signed EAS build, and physical-device QA are not yet evidenced. External pilot and real patient data remain prohibited.

## Sprint 22 mobile/cloud preparation

EAS internal profiles and cloud target options are documented, but no public deployment has been performed. Production remains blocked on a non-default secret, exact CORS origins, private media storage, consent/privacy approval, auth/role verification, retention/deletion enforcement, monitoring/audit operations, and physical-device QA. See `cloud_deployment_preparation.md` and `privacy_security_release_checklist.md`.

## Roadmap position

Cloud deployment is Sprint 17. It comes after API hardening, the Sprint 13 auth/privacy foundation, the mobile API contract, stable database/session behavior, and clear dataset/model registries. Container preparation supports local engineering but does not mean the product is ready for internet-facing patient use.

## Local and container development

```powershell
python -m pip install -r backend/requirements.txt
Set-Location backend
python -m uvicorn app.main:app --reload
```

```powershell
docker compose build
docker compose up
```

SQLite and local artifacts are development-only. A production-like deployment should use managed PostgreSQL, private expiring object storage, migrations, backups, and least-privilege service credentials.

## Sprint 17 production requirements

- Authentication and role-based authorization for patient, therapist, and administrator boundaries.
- A secure database with migrations, encrypted transport/storage, backup and recovery.
- Private media/object storage with signed expiry, retention, deletion, and access auditing.
- Environment-managed secrets and explicit production CORS origins.
- Structured privacy-conscious logging, monitoring, alerting, health/readiness probes, and incident response.
- Consent workflow, privacy review, data inventory, retention policy, and user deletion/export behavior before real patient data.
- Performance, cost, accessibility, dependency, vulnerability, and disaster-recovery review.

Render, Railway, Fly.io, or Azure App Service may support early pilots; AWS may follow when operational needs justify it. Hosting choice does not establish clinical validation or privacy compliance.

## Current restriction

No real patient data is permitted in development or demo mode. Use synthetic, consented research data under an approved process, or non-identifiable evaluation data. The product supports exercise monitoring and does not diagnose or prescribe treatment.

Sprint 13 JWT auth is a development foundation. Production still needs verification, recovery, MFA/risk controls where appropriate, refresh/revocation strategy, rate limiting, operational audit review, and identity-provider/security assessment.
