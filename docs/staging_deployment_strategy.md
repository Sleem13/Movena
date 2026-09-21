# Staging deployment strategy

Use the [AWS-only deployment workflow](aws_api_routing.md): CloudFront/S3 for the
website, ALB/ECS for FastAPI, RDS for PostgreSQL, and Secrets Manager for credentials.
Terraform and the GitHub Actions workflow define the active configuration.
Do not provision duplicate Render, Vercel, or separate database deployments.

The environment is internal staging. Use synthetic or non-identifying test media.
Keep authentication, consent, artifact retention, and physical-device validation
as release gates. A successful infrastructure deployment does not establish clinical readiness.
