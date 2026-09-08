# Sprint 24 Private Staging Deployment Environment Safety

Movena keeps staging and production deployment validation fail-closed. Both environments require a non-default `SECRET_KEY` of at least 32 characters, explicit HTTPS CORS origins, authenticated analysis, and disabled public demo mode. `validate_deployment_safety()` remains active when the FastAPI application is imported.

## Pytest isolation

Repository-level pytest runs use `APP_ENV=test`. `tests/conftest.py` assigns the complete test environment before test modules can import `app.main`, including a test-only secret, localhost CORS origins, disabled analysis authentication, enabled demo behavior, and the isolated `sqlite:///./test_movena.db` database. The generated database is removed at the end of the test session.

This isolation prevents a shell containing `APP_ENV=staging` or incomplete staging secrets from making test collection nondeterministic. Test values are not valid deployment values and must never be copied into staging or production. Secret values and database credentials must not be written to application logs.

## Local and device testing

Use `APP_ENV=development` for local browser, emulator, or phone/LAN testing where the API is reached over localhost or a private HTTP LAN address. Use `APP_ENV=staging` only after a real HTTPS staging API and HTTPS frontend origin are available. Never weaken staging CORS or secret validation to accommodate local phone testing.

Run the isolated suite from the repository root:

```powershell
python -m pytest
```
