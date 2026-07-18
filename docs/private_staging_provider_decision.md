# Private Staging Provider Decision

## Selected path

Use Render for one private/internal FastAPI web service built from the root Dockerfile, Neon PostgreSQL for the staging database, Vercel for the Vite web client, and EAS `preview-staging` for Android internal distribution. This matches the existing Docker, SQLAlchemy/Psycopg, Vite, and Expo structure with minimal infrastructure maintenance.

No provider credentials or staging database URL are available in this workspace, so no service was provisioned. The exact steps are documented in the backend, PostgreSQL, web, secrets, and mobile staging guides. No public release occurred.

## Limitations

- Render/Vercel URLs are internet-routable even when intended for internal use; provider access controls and application authentication must restrict use.
- Local backend artifact storage requires one instance and is temporary. It is unsuitable for scaling or real patient data.
- `init_db()` creates schema but is not a versioned migration system.
- EAS build cannot begin until a real staging API URL exists in its preview environment.

## Rollback

1. Disable the Render service or set it to zero instances and revoke its database credential.
2. Disable the Vercel staging deployment/domain.
3. Revoke EAS internal install links/build access where available.
4. Rotate `SECRET_KEY`, admin password, provider tokens, and database credential.
5. Delete staging artifacts and destroy/reset the Neon staging branch/database.
6. Preserve only non-identifying incident evidence and record the rollback decision.
