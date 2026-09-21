# Backend staging deployment

Use [the AWS deployment workflow](aws_api_routing.md). The root Dockerfile runs
Alembic migrations before starting FastAPI in ECS. The workflow manages the existing
Terraform stack and publishes the website only after backend readiness succeeds.

Keep database credentials, signing keys and admin credentials in AWS Secrets Manager.
Terraform defines non-secret settings, exact allowed origins and the frontend URL.
Do not use the retired multi-provider setup or initialize the live database with `create_all()`.

Verify `/health`, `/ready`, authentication, account creation and application-specific
flows after changes. Use synthetic records for testing and pause test accounts afterward.
Configure SMTP before testing email delivery with users; console delivery writes links
to restricted backend logs. Review artifact retention and access controls separately.
