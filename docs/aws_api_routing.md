# Movena deployment source of truth

AWS is authoritative: Terraform `application_url` -> GitHub Actions
`VITE_API_BASE_URL` -> CloudFront (S3 frontend, `/api/*` ALB/ECS backend) -> RDS.
Do not copy a historical hostname into application source. Resolve the current
value with `terraform -chdir=infra/aws output -raw application_url` against the
existing remote state configured by the deployment workflow.

## Diagnosis and audit (2026-09-20)

The public Vercel bundle was independently fetched and contains the old Render API URL. No Render fallback
exists in the checked-in frontend client, Vite config, package scripts, or
`frontend/vercel.json`; only example env files exist under `frontend/` locally.
The URL therefore comes from that deployment's build environment or supplied env
file, rather than an application fallback. The exact provider setting is not
verified: the connected Vercel project-settings tool fails schema validation.
Old guides and root staging examples actively recommended Render. The prior
runtime-only check allowed Vite to compile missing/incorrect values successfully.
Vite substitutes client env values at build time; an environment edit alone
does not repair an already published bundle.

Vercel production deployment `dpl_8Pne5KJriaNHfE7pRNQhYb64b7XZ` uses current main
commit `31c6437`, with Git metadata still naming `Sleem13/PhysioVision-AI`.
Confirm the project's Git integration targets `Sleem13/Movena` and root directory
`frontend`. The local origin URL also uses the old GitHub redirect.

Reference audit covers tracked files for `physio-vision`, `physiovision`, both
legacy Render API names, `render.com`/`onrender.com`, both public API variables,
and the old CloudFront hostname. Remaining references are classified as:

- AWS IAM prefixes: retained resource identities; do not cosmetically rename
  them or alter the remote state key. The old diagnostic workflow targets
  `physiovision-staging`; use the active Terraform ECS outputs and log group
  when investigating Movena, rather than assuming that old cluster is current.
- Docker volume/database migration compatibility, mobile EAS slug/project ID,
  extractor compatibility alias: retained to avoid breaking existing users/data.
- Notebook, benchmark, sprint and deployed-test reports: historical evidence,
  not deployment instructions. Older mobile build reports do not describe current EAS config.
- Render manifest: retained as legacy/optional rollback material, not the web target.
- CORS and rejection tests: intentional regression fixtures.

## Deploy and verify

The AWS workflow starts RDS if stopped, requires availability, sets ECS desired
count to one, waits for stability and JSON `/ready` status, then builds with the
Terraform URL, uploads S3 assets, invalidates CloudFront and smoke-tests readiness
and the proxied exercises API. Run `bash infra/aws/smoke-test.sh "$APPLICATION_URL"`
for the same read-only checks. This patch does not run Terraform apply.

On 2026-09-20, `https://d1ylxhoq5y66vd.cloudfront.net/ready` returned 200 with
`status=ready` and `database_connection=ok`; `/api/v1/exercises` returned 200.
That URL is already configured in mobile EAS. The historical
`d139746brwkxwp.cloudfront.net` did not resolve from the verification machine.
Confirm the current Terraform output before adopting the reachable URL.
Unauthenticated `/api/v1/admin/users` returned 401; authenticated admin database
access remains unverified. Do not declare the incident resolved on these checks alone.

## Retaining Vercel

Set `VITE_API_BASE_URL` in both intended Production and Preview scopes to the
verified AWS `application_url`, removing branch-specific Render overrides, and
rebuild/redeploy. Builds now reject missing, malformed and Render endpoints.
The catch-all Vercel SPA rewrite stays unchanged because API calls use an
explicit absolute origin. Local `npm run dev` retains localhost defaults;
local builds can explicitly supply `http://127.0.0.1:8000`.

Set GitHub repository variable `AWS_ADDITIONAL_CORS_ORIGINS` to a JSON list of
explicit retained frontend origins, for example `["https://physio-vision-ai.vercel.app"]`.
It defaults to `[]`. A reviewed AWS deployment must apply it before browser access
from Vercel works. Add exact preview origins only when needed; do not use a wildcard.

## IAM and repository rename

The bootstrap script already defaults to `Sleem13/Movena` and main-branch trust.
That does not update live IAM. An AWS administrator must inspect the role selected
by `AWS_DEPLOY_ROLE_ARN`: trust must permit
`repo:Sleem13/Movena:ref:refs/heads/main`, with audience `sts.amazonaws.com`.
If it still trusts the old name, update that existing role. Do not create a new
role/state bucket accidentally by accepting unrelated bootstrap defaults.
The bootstrap inline policy now matches Terraform's preserved
`physiovision-movena-*` names. Review existing permissions before re-running
`bootstrap-github-oidc.ps1` with the actual account, role and state bucket.
Live trust/permissions were not accessible in this session and remain unverified.

## Database and administration

ECS receives host, port and database name from RDS outputs; username/password are
injected from the RDS-managed secret JSON fields. No `DATABASE_URL` override is
set in the task definition. `database_url_from_environment` encodes credentials
and constructs a `postgresql+psycopg` URL; an explicitly supplied `DATABASE_URL`
would take precedence. All seven admin user routes use the shared `get_db` session.
The frontend admin client uses the same configured Axios instance as other APIs.

`backend/app/main.py:database_exception_handler` catches `SQLAlchemyError`, logs
the exception and traceback (including the driver exception), and returns 503
with `DATABASE_UNAVAILABLE`; recognized missing-schema OperationalErrors instead
return `DATABASE_SCHEMA_OUTDATED`. Logging already provides CloudWatch diagnostics.

After deployment, sign in with an authorized administrator and verify GET users
and detail against AWS. Verify create/status/role/password/delete with a designated
disposable test account in staging; never alter real users for a smoke test.
Local tests are not proof of deployed RDS-backed administration.

## Mobile, rollback and Render retirement

Expo independently uses `EXPO_PUBLIC_API_BASE_URL`; existing EAS AWS configuration,
project identity and development resolution remain unchanged. Confirm EAS remote
env values when rebuilding, since repository values do not update EAS settings.

Rollback by reverting this PR and restoring a previously verified AWS build and
its explicit environment value. This patch changes no database data, Terraform
state keys or resource names. Retain Render until authenticated AWS administration,
browser CORS, deployed frontend API origin and any mobile consumers are verified.
Only then retire Render after checking remaining consumers and retention needs.

## Patch validation

- Backend full suite: 459 passed. After adding deployment guards, focused deployment/rebrand suite: 13 passed.
- Frontend: `npm ci` succeeded; 31 test files / 182 tests passed.
- Production build with the reachable AWS URL succeeded. Missing URL and legacy Render URL builds failed with clear configuration errors, as expected.
- Built JavaScript contains neither known legacy Render API URL.
- New shell smoke test passed against the reachable CloudFront endpoint.
- Terraform `fmt -check` and `validate` passed after `init -backend=false`; no apply or live IAM update was performed.
- npm reported 6 dependency advisories; existing frontend media mocks/chunk-size and Python deprecation/cache warnings did not fail validation.

## Exact modified files

- `.env.production.example`
- `.env.staging.example`
- `.gitattributes`
- `.github/workflows/deploy-aws.yml`
- `README.md`
- `backend/.env.staging.example`
- `docs/aws_api_routing.md`
- `docs/deployed_staging_smoke_test_results.md`
- `docs/frontend_staging_deployment.md`
- `docs/operational_staging_activation_plan.md`
- `docs/web_frontend_staging_deployment.md`
- `frontend/.env.production.example`
- `frontend/.env.staging.example`
- `frontend/buildConfig.test.js`
- `frontend/src/config/apiConfig.js`
- `frontend/src/config/apiConfig.test.js`
- `frontend/src/config/resolveApiBaseUrl.js`
- `frontend/vite.config.js`
- `infra/aws/README.md`
- `infra/aws/bootstrap-github-oidc.ps1`
- `infra/aws/main.tf`
- `infra/aws/smoke-test.sh`
- `infra/aws/variables.tf`
- `mobile/README.md`
- `render.yaml`
- `tests/test_aws_deployment_safety.py`
- `tests/test_rebrand_configuration.py`
