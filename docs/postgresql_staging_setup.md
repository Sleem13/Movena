# PostgreSQL staging setup

The active database is AWS RDS, managed by `infra/aws`. Follow
[the AWS deployment guide](aws_api_routing.md) and use the existing remote state.
Do not provision a parallel database for this environment.

Database credentials belong in AWS Secrets Manager. The application uses SQLAlchemy
with Psycopg 3. Never commit or print connection strings or database passwords.
The container runs `alembic upgrade head` before starting the API; migrations are
versioned in `backend/alembic/versions`.

Verify `/ready` reports `database_connection=ok`, then verify an authenticated workflow.
Review TLS, backups and restore procedures independently. Restore into an isolated
instance for rehearsal; do not reset or destroy the live database during routine deployment.
