# PostgreSQL Staging Setup

## Execution status — 2026-07-19

**Blocked before provisioning.** `DATABASE_URL` and `NEON_API_KEY` are unset, no Neon project/branch identifier is configured, and no Neon CLI is installed. Consequently no managed PostgreSQL instance was created, no schema was initialized, no administrator/beta account was seeded, and no backup or restore was executed. These are pending operational steps, not passes. No real patient data was accessed or introduced.

Create a dedicated Neon project or branch named for PhysioVision AI staging. Do not connect production or patient databases. Require TLS and restrict administrative access.

Use the provider connection string as `DATABASE_URL`. Common `postgresql://` or `postgres://` URLs are normalized to SQLAlchemy's Psycopg 3 dialect. If writing it explicitly:

```text
postgresql+psycopg://USER:PASSWORD@HOST/DATABASE?sslmode=require
```

Set the URL only in Render/provider secrets. Initialize a new disposable schema:

```powershell
cd backend
..\.venv\Scripts\python.exe -c "from app.db.database import init_db; init_db()"
```

From the repository root, set `ADMIN_EMAIL`, an `ADMIN_PASSWORD` containing at least 8 characters, and a non-identifying name, then run `python scripts/seed_admin_user.py`. Verify `/ready` reports an available database without printing the connection URL.

For reset, revoke active credentials, destroy/recreate the staging branch/database, issue a new credential, rerun initialization, and reseed the admin. Use provider backups/point-in-time restore and test restoration into a separate staging branch. Current `create_all()` initialization has no ordered upgrades or rollback; Alembic is required before long-lived production evolution.

Before beta invitations, record the managed database identifier (not its credential), TLS verification, schema initialization timestamp, seeded non-identifying beta account owner, backup policy, a sanitized restore-test result, and the person approving reset/deletion access. Store credentials only in provider secret stores.
