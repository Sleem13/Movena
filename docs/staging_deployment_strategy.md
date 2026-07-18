# Staging Deployment Strategy

PhysioVision AI staging is an internal engineering environment. It is not a public pilot, medical service, or patient-record system. Use synthetic or explicitly non-identifiable test recordings only.

## Recommended path: managed single-instance staging

For the current monorepo, use the existing root Dockerfile on Render or Railway for one FastAPI instance, Vercel or Netlify for `frontend/`, and Neon or Supabase PostgreSQL. Keep backend artifacts on a single-instance temporary/persistent disk for this internal stage only. Report and overlay URLs are short-lived HMAC-signed when protected analysis is enabled. Do not scale to multiple backend instances while artifacts remain local.

This path minimizes operations while preserving the existing FastAPI, Vite, and SQLAlchemy structure. Configure HTTPS backend/web domains, exact frontend CORS origin, provider secrets, database TLS, one internal admin, health checks at `/health`, and readiness checks at `/ready`.

Alternative managed providers are Fly.io and Azure App Service. A private-VM alternative may run `docker compose build` and `docker compose up`, but the checked-in Compose file remains a local-development profile; staging must supply a separate secret environment, HTTPS reverse proxy, PostgreSQL, backups, restricted firewall, and private access controls.

## Deployment order

1. Create an empty staging PostgreSQL database and private backend service.
2. Set every value from `backend/.env.staging.example` in the provider; never upload the populated file.
3. Start one backend instance and verify `/health` and `/ready`.
4. Seed one non-identifying internal admin through provider secrets.
5. Deploy the Vite build with its exact HTTPS backend URL.
6. Set backend CORS to the exact staging web origin and redeploy.
7. Configure EAS preview environment variables and build `preview-staging` internally.
8. Execute the smoke, security, artifact-retention, and physical-device matrices.

The Docker image disables Uvicorn access logs so signed artifact query credentials are not written by the application server. Configure the hosting proxy to redact query strings and restrict log access as well; provider ingress logging is outside the application process.

External testers remain blocked until auth, consent, privacy policy, private storage, retention/deletion, physical-device QA, and professional safety review are complete.
