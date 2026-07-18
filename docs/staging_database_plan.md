# Staging Database Plan

## Sprint 24 status

PostgreSQL code/driver support and exact setup/reset instructions are complete, but no Neon database or `DATABASE_URL` credential was available. Actual schema initialization, seed, TLS, backup, and restore validation are blocked. See `postgresql_staging_setup.md`.

Use a small managed PostgreSQL database from Neon or Supabase; Railway PostgreSQL is also compatible. Require TLS, provider access controls, a unique staging credential, and automated backups where available. `postgresql://` and `postgres://` provider URLs are normalized to SQLAlchemy's `postgresql+psycopg://` driver, and Psycopg 3 binary support is included.

## Initialization and admin seed

The current startup calls `init_db()`, which uses SQLAlchemy `Base.metadata.create_all()`. There is no Alembic migration history, so apply this only to a new disposable staging database after reviewing the schema.

```powershell
$env:APP_ENV="staging"
$env:DATABASE_URL="postgresql+psycopg://..."
$env:SECRET_KEY="<provider-secret-at-least-32-characters>"
$env:CORS_ALLOWED_ORIGINS="https://staging-web.example.com"
$env:REQUIRE_AUTH_FOR_ANALYSIS="true"
$env:ENABLE_PUBLIC_DEMO_MODE="false"
cd backend
..\.venv\Scripts\python.exe -c "from app.db.database import init_db; init_db()"
```

Set `ADMIN_EMAIL`, a unique strong `ADMIN_PASSWORD`, and non-identifying `ADMIN_FULL_NAME`, then run `python scripts/seed_admin_user.py` from the repository root. Never print or commit the password.

## Backup, restore, and reset

- Use provider point-in-time recovery or scheduled encrypted backups; test restore into a separate staging database.
- Before a reset, export only approved non-identifying fixtures if needed, destroy the staging database, create a new database/credential, initialize the schema, and reseed the admin.
- Rotate credentials after staff changes or suspected exposure.
- Never copy production/patient data into staging.

The absence of versioned migrations is a staging limitation. Add Alembic before production or any long-lived schema evolution.
