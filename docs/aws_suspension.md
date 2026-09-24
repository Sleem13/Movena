# AWS staging suspension — 2026-09-24

The owner requested suspension until further instruction. Do not resume deployment
or start the app without an explicit request from the owner.

- GitHub repository variable `AWS_SUSPENDED=true` blocks the deployment jobs.
- The `deploy-aws.yml` workflow is disabled in GitHub.
- `suspend-aws.yml` performs a read-only inventory by default; its `apply` input
  stops ECS tasks and RDS, disables CloudFront, and removes only the stateless ALB.
- An hourly stop-only GitHub workflow rechecks suspension because AWS automatically
  restarts stopped RDS instances after seven days. It never starts resources.
- Database contents, EFS files, S3 objects, ECR images, secrets and Terraform state
  are preserved. Storage, backups and secret retention still incur charges.

This is intentional operational drift from the active Terraform configuration.
Do not apply Terraform while suspended: it would recreate the load balancer and
restart the application. The CloudFront hostname and persistent data are retained.

GitHub schedules can be delayed and public-repository schedules can be disabled
after 60 days without repository activity. This guard is not a guarantee of zero
database runtime charges after an automatic restart. Review longer-term archival
options with the owner if suspension will be extended; never delete data silently.

## Authorized resume procedure

1. Obtain the owner's explicit instruction to resume.
2. Disable the stop-only workflow and wait for any running suspension job to finish.
3. Set `AWS_SUSPENDED=false` and enable `deploy-aws.yml`.
4. Dispatch the normal AWS deployment workflow. Terraform recreates the ALB/listener,
   restores CloudFront's origin, reenables serving and restores the ECS desired count.
   The deployment workflow starts RDS and waits for database/backend readiness.
5. Verify health, database readiness, login and the requested application workflows.

AWS reference: https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/USER_StopInstance.html
