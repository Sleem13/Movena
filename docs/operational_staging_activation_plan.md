# Operational staging activation

Follow [the AWS deployment guide](aws_api_routing.md). The active AWS stack already
hosts the website, API and database; do not recreate the former multi-provider stack.

1. Review the existing AWS role, remote state and Secrets Manager configuration.
2. Push tested changes to `main` and follow the AWS GitHub Actions workflow.
3. Confirm `/health` reports the expected commit and `/ready` reports database readiness.
4. Run the CloudFront smoke script and an authenticated synthetic account workflow.
5. Configure mobile clients with the same verified AWS application URL and complete device QA.

Never print database credentials, signing keys, admin passwords, JWTs or signed artifact URLs.
For rollback, revert the faulty change and deploy through the same workflow. Do not destroy
or reset the database as part of an application rollback.
