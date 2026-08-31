# PhysioVision AI on AWS

This stack deploys the current application without rewriting its analysis pipeline:

- CloudFront provides the public HTTPS application URL and proxies API/WebSocket traffic.
- A private S3 bucket stores the Vite build and is readable only through CloudFront OAC.
- ECS Fargate runs the FastAPI/OpenCV/MediaPipe container behind an Application Load Balancer.
- RDS PostgreSQL is private, encrypted, backed up, and uses an AWS-managed master password.
- EFS provides encrypted persistent storage for temporary reports and annotated overlays.
- Secrets Manager injects the JWT and protected administrator credentials at runtime.
- CloudWatch receives container logs and ECS Container Insights.
- EventBridge Scheduler suspends staging ECS and RDS outside Cairo weekday working hours.

The initial deployment defaults to `staging`. Production mode is intentionally blocked by the application until SMTP delivery is configured.

## Prerequisites

1. An AWS account with permission to create IAM, VPC, ECS, ECR, ELB, RDS, EFS, S3, CloudFront, CloudWatch, and Secrets Manager resources.
2. AWS CLI v2 authenticated with AWS IAM Identity Center or another short-lived credential method.
3. Docker Desktop running, Terraform 1.7+, Node.js, and npm.
4. A reviewed AWS budget and billing alarm. This is not a free-tier-only stack.

Authenticate without placing long-lived keys in the repository:

```powershell
aws configure sso
aws sso login --profile your-profile
$env:AWS_PROFILE = "your-profile"
aws sts get-caller-identity
```

## Preview and deploy

The first non-mutating run verifies identity and shows the Terraform plan if the application secret already exists:

```powershell
.\infra\aws\deploy.ps1 -Region eu-central-1 -Environment staging
```

The apply flow creates a missing secret interactively, bootstraps ECR, builds and scans the backend image, displays the complete Terraform plan, and waits for the exact confirmation word `DEPLOY` before creating the main stack:

```powershell
.\infra\aws\deploy.ps1 -Region eu-central-1 -Environment staging -Apply
```

The script never writes the administrator password or JWT key into the repository or Terraform variables. Terraform state is stored in a private, versioned, encrypted S3 backend with native state locking.

## GitHub Actions deployment

The preferred deployment path is `.github/workflows/deploy-aws.yml`. It runs backend and frontend tests, assumes an AWS role through GitHub OIDC, builds an immutable ECR image, applies the reviewed Terraform stack, publishes the frontend, and verifies `/ready`.

Bootstrap the state bucket and repository-scoped OIDC role once from a short-lived AWS administrator session:

```powershell
.\infra\aws\bootstrap-github-oidc.ps1
```

Configure these GitHub Actions repository variables with the script output and the existing runtime secret ARN:

- `AWS_DEPLOY_ROLE_ARN`
- `TF_STATE_BUCKET`
- `APP_SECRET_ARN`

The OIDC trust is restricted to this repository's `main` branch. No AWS access key is stored in GitHub.

## Production promotion gates

Do not change `Environment` to `production` until all of these are complete:

- Verify a sending domain/address in Amazon SES and request production sending access.
- Add `SMTP_USERNAME` and `SMTP_PASSWORD` to the existing application secret.
- Set `email_delivery_mode = "smtp"`, `email_from`, and the regional SES SMTP endpoint.
- Add a custom Route 53/ACM domain if a branded URL is required.
- Add AWS WAF rate limiting and managed protections for external public use.
- Run `alembic upgrade head` with the migration owner and verify revision `0003_data_rights` before starting the application.
- Add Daily and Paymob credentials to Secrets Manager only if those feature flags are approved; never expose them to Web or Expo builds.
- Complete the privacy, consent, retention, deletion, incident-response, and legal review before processing identifiable patient data.
- Complete every evidence item in `docs/care_platform_launch_gate.md`; local automated tests alone are not a release approval.
- Load-test 100 MB uploads and the synchronous analysis duration. If analyses exceed the CloudFront/origin response window, move analysis to an asynchronous SQS worker workflow.

## Operational notes

- The default task size is 2 vCPU / 4 GiB because pose analysis is CPU-heavy.
- Staging starts its database at 07:45 and ECS service at 08:00 Monday-Friday, then stops ECS at 20:00 and RDS at 20:15 every day (`Africa/Cairo`). The static frontend remains available, but API features are unavailable while staging is suspended. Deployments temporarily wake the stack and restore the scheduled state afterward.
- The stack deliberately avoids a NAT Gateway: Fargate tasks use public IPs with no inbound access except through the ALB security group. RDS remains in private subnets.
- The ALB accepts traffic only from the AWS-managed CloudFront origin-facing prefix list.
- Artifacts remain protected by application authorization/signatures and expire according to application retention settings.
- `protect_data = true` enables RDS and ALB deletion protection and a final database snapshot.

## Teardown

Teardown is intentionally not automated. Disable deletion protection only after taking and verifying backups, then review a Terraform destroy plan carefully. S3 versions, ECR images, EFS data, Secrets Manager secrets, and RDS snapshots may require explicit retention or cleanup decisions.
