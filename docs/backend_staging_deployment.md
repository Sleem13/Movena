# Backend Private Staging Deployment

## Render procedure

1. Create a Render Web Service from the repository using Docker and the root `Dockerfile`.
2. Restrict team access and do not advertise the URL.
3. Add variables from `backend/.env.staging.example` through Render secrets.
4. Attach the Neon `DATABASE_URL`, exact Vercel HTTPS origin, and strong secret.
5. Use the Docker command already defined; it runs Uvicorn on `0.0.0.0:8000` with access logs disabled.
6. Configure health checking against `/ready` and one instance only while artifacts are local.
7. Initialize schema and seed the internal admin through a one-off shell with secrets injected.
8. Schedule `python scripts/cleanup_artifacts.py --retention-hours 24` and monitor disk usage.

The alternative private-VM rehearsal file `docker-compose.staging.yml` requires PostgreSQL, secret, and exact CORS values and binds the backend to loopback for a private reverse proxy.

After deploy, validate `/health`, `/ready`, login, exercises, auth enforcement, upload validation, all five analyzers with non-identifying samples, rejected input, session ownership, signed artifact access/expiry, and cleanup. Provider deployment is currently blocked because no Render token/account configuration or Neon database URL is available.

Local container status: `docker-compose.staging.yml` passed configuration validation with placeholder test values. Image build was attempted but Docker Desktop's daemon/service was stopped and could not be started from the current non-administrative session, so no new image was produced.
