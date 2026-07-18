# PostgreSQL Staging Setup

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

From the repository root, set `ADMIN_EMAIL`, a unique 14+ character mixed-case/numeric `ADMIN_PASSWORD`, and a non-identifying name, then run `python scripts/seed_admin_user.py`. Verify `/ready` reports an available database without printing the connection URL.

For reset, revoke active credentials, destroy/recreate the staging branch/database, issue a new credential, rerun initialization, and reseed the admin. Use provider backups/point-in-time restore and test restoration into a separate staging branch. Current `create_all()` initialization has no ordered upgrades or rollback; Alembic is required before long-lived production evolution.
