# API hardening

Uploads are limited by configured size, safe basename, supported extension, declared media type, and non-empty content. Supported extensions are MP4, MOV, AVI, MKV, and WebM. Failures use the shared `{status, error_code, message, details}` contract with codes including `FILE_TOO_LARGE`, `UNSUPPORTED_FILE_TYPE`, `EMPTY_FILE`, and `INVALID_FILENAME`.

`GET /health` reports non-secret application, database, artifact-directory, environment, and feature status. `GET /ready` actively checks the database and temporary artifact write access and returns 503 when unavailable. It does not expose connection strings or credentials.

Temporary artifacts can be inspected with `python scripts/cleanup_artifacts.py --dry-run` and removed according to `ARTIFACT_RETENTION_HOURS` without touching files outside `backend/artifacts/overlays` and `backend/artifacts/reports`.

Before production: add HTTPS, authentication and authorization, request throttling, malware/content inspection, structured audit logging, object storage, managed PostgreSQL, secrets management, and a formal privacy/security review.
