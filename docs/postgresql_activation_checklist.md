# PostgreSQL Activation Checklist

## Current status

**Blocked / inactive.** No managed Neon database, project identifier, credential, or `DATABASE_URL` is available. Schema initialization, beta account seeding, backup, and restore have not run. No real patient data is permitted.

## Provisioning gate

- [ ] Create a dedicated staging project/branch; never connect a production or patient database.
- [ ] Restrict provider administration to named authorized owners.
- [ ] Require TLS and use a connection string with `sslmode=require`.
- [ ] Store `DATABASE_URL` only in Render/provider secret storage.
- [ ] Confirm `DATABASE_URL` uses the dedicated staging database and Psycopg-compatible form.

```text
postgresql+psycopg://<user>:<password>@<host>/<database>?sslmode=require
```

## Schema initialization

Run from an authorized administrative environment with staging variables loaded. Do not echo the connection string.

```powershell
$env:APP_ENV = "staging"
$env:DATABASE_URL = "<set through a secure shell or provider secret injection>"
$env:SECRET_KEY = "<unique 32+ character staging secret>"
$env:CORS_ALLOWED_ORIGINS = "https://<exact-staging-frontend-domain>"
$env:REQUIRE_AUTH_FOR_ANALYSIS = "true"
$env:ENABLE_PUBLIC_DEMO_MODE = "false"
cd backend
..\.venv\Scripts\python.exe -c "from app.db.database import init_db; init_db()"
```

- [ ] Record a sanitized schema initialization timestamp and operator.
- [ ] Verify `/ready` reports the database as available without exposing credentials.
- [ ] Record the current limitation: initialization uses `create_all()` rather than versioned Alembic migrations.

## Seed an administrative beta account

Use a non-identifying staging alias/email and a unique 14+ character password containing upper-, lower-case, and numeric characters. Run from the repository root:

```powershell
$env:ADMIN_EMAIL = "<non-identifying-staging-admin-alias>"
$env:ADMIN_PASSWORD = "<strong unique value from secret storage>"
$env:ADMIN_FULL_NAME = "Staging Beta Administrator"
python scripts/seed_admin_user.py
```

- [ ] Store the password outside the repository and ordinary logs.
- [ ] Verify login and role behavior with the seeded account.
- [ ] Create additional beta users only when operational GO and consent workflow permit it.

## Backup, restore, and reset

- [ ] Enable the provider's encrypted backup or point-in-time recovery appropriate to the staging plan.
- [ ] Test restore into a separate disposable staging branch; never overwrite the active branch for a drill.
- [ ] Record recovery point, restore duration, operator, and sanitized outcome.
- [ ] Reset by revoking credentials, destroying/recreating the staging branch, issuing a new credential, initializing schema, and reseeding only necessary non-identifying accounts.
- [ ] Verify provider logs/backups and deletion limitations before external beta.
- [ ] Never copy real patient, production, diagnosis, treatment, or sensitive health data into staging.

## Closure evidence

This gate passes only when the database is reachable over TLS, schema and seed commands succeed, `/ready` passes, backup/restore is evidenced, least-privilege access is reviewed, and no real patient data exists.
