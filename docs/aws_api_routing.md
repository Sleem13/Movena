# Movena deployment source of truth

> AWS staging is suspended at the owner's request from 2026-09-24. Do not deploy or
> start resources until explicitly instructed. See [the suspension procedure](aws_suspension.md).

AWS is the only active deployment target. The current website and API are at
https://d1ylxhoq5y66vd.cloudfront.net. Resolve the authoritative URL from the
existing remote state with `terraform -chdir=infra/aws output -raw application_url`;
do not hardcode historical hostnames into application source.

## Deployment path

`.github/workflows/deploy-aws.yml` verifies backend and frontend tests, publishes
an immutable commit-tagged ECR image, applies Terraform, waits for ECS and database
readiness, then builds the frontend with the Terraform URL and publishes it to S3.
CloudFront serves the website and routes `/api/*` to ALB/ECS. RDS stores application data.
The workflow finishes with `infra/aws/smoke-test.sh`.

Push application changes to `main` to deploy. Manual workflow dispatch can redeploy
the same commit; image reuse preserves the full ECR repository path (`movena/backend`).
Do not run a second deployment provider for this environment. The Vercel project
`physio-vision-ai` and its deployment configuration were deleted on 2026-09-21.
The obsolete Render blueprint has also been removed. AWS is the sole web deployment target.

## Runtime configuration

Backend credentials belong in AWS Secrets Manager. GitHub repository variables select
the existing deploy role, Terraform state bucket and application secret ARN.
`VITE_API_BASE_URL` is public build configuration supplied by the workflow.
The frontend build rejects missing, malformed and legacy Render API endpoints.

The AWS website and API share an origin. `AWS_ADDITIONAL_CORS_ORIGINS` is `[]`.
Only add an explicit HTTPS origin when a separate client deployment is intentionally retained.
Changing the variable requires a workflow run to apply it.

## GitHub OIDC trust

The current role is `PhysioVisionGitHubDeploy` in account `720466551087`.
GitHub uses an immutable subject prefix for this renamed repository. Query it before
changing trust or running bootstrap:

```powershell
gh api repos/Sleem13/Movena/actions/oidc/customization/sub
```

The verified main-branch subject is
`repo:Sleem13@236138703/Movena@1295797057:ref:refs/heads/main`.
The audience remains `sts.amazonaws.com`. Bootstrap accepts `OidcSubjectPrefix`,
checks that it matches `Repository`, and preserves the narrow IAM resource naming boundary.
When maintaining the existing stack, pass its actual role and state bucket names;
do not create a parallel stack using bootstrap defaults.
See [GitHub immutable subject documentation](https://docs.github.com/en/actions/reference/security/oidc#immutable-subject-claims).

## Verification

Run `bash infra/aws/smoke-test.sh <application_url>` to check readiness and the proxied API.
`/health` reports the deployed commit and database status. Also verify an authenticated
admin workflow; public health endpoints alone do not prove patient creation works.
On 2026-09-21, the patient-creation fix returned HTTP 201, account details and patient
profile returned HTTP 200, and the synthetic account was paused after testing.
