from urllib.parse import parse_qs, urlparse
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient

from app.api.dependencies.auth import AuthError
from app.api.routes.artifacts import authorize_artifact
from app.core.config import Settings, database_url_from_environment, get_settings, normalize_database_url
from app.services.artifact_service import build_artifact_url
from app.main import app


def safe_staging_settings(**overrides):
    values = {
        "app_env": "staging",
        "secret_key": "staging-only-secret-that-is-longer-than-32-characters",
        "cors_allowed_origins": ["https://staging.example.com"],
        "require_auth_for_analysis": True,
        "enable_public_demo_mode": False,
        "email_delivery_mode": "smtp",
        "smtp_host": "smtp.example.com",
        "email_from": "no-reply@example.com",
        "frontend_url": "https://staging.example.com",
        "clinical_organization_name": "Example Rehabilitation Organization",
        "clinical_escalation_contact": "+20-000-000-0000",
    }
    values.update(overrides)
    return Settings(**values)


def test_safe_staging_config_validates():
    safe_staging_settings().validate_deployment_safety()


def test_staging_console_email_mode_does_not_require_smtp():
    settings = safe_staging_settings(
        email_delivery_mode="console",
        smtp_host="",
        frontend_url="http://localhost:5173",
    )

    settings.validate_deployment_safety()


def test_staging_smtp_requires_delivery_settings_and_https_frontend():
    settings = safe_staging_settings(
        smtp_host="",
        email_from="invalid",
        frontend_url="http://localhost:5173",
    )

    with pytest.raises(RuntimeError, match="SMTP delivery requires"):
        settings.validate_deployment_safety()


def test_production_rejects_console_email_mode():
    settings = safe_staging_settings(
        app_env="production",
        database_url="postgresql://user:password@db.example.com/physiovision",
        email_delivery_mode="console",
        require_email_verification=True,
    )

    with pytest.raises(RuntimeError, match="production email verification requires"):
        settings.validate_deployment_safety()


def test_production_allows_console_mode_when_email_verification_is_suspended():
    settings = safe_staging_settings(
        app_env="production",
        database_url="postgresql://user:password@db.example.com/physiovision",
        email_delivery_mode="console",
        require_email_verification=False,
    )

    settings.validate_deployment_safety()


def test_production_rejects_local_or_missing_database():
    settings = safe_staging_settings(app_env="production", database_url="sqlite:///local.db")

    with pytest.raises(RuntimeError, match="production DATABASE_URL must use PostgreSQL"):
        settings.validate_deployment_safety()


def test_production_requires_clinical_escalation_configuration():
    settings = safe_staging_settings(
        app_env="production",
        database_url="postgresql://user:password@db.example.com/physiovision",
        clinical_organization_name="Your organization",
        clinical_escalation_contact="",
    )

    with pytest.raises(RuntimeError, match="clinical escalation organization and contact"):
        settings.validate_deployment_safety()


def test_staging_requires_clinical_escalation_configuration():
    settings = safe_staging_settings(
        clinical_organization_name="Your organization",
        clinical_escalation_contact="",
    )

    with pytest.raises(RuntimeError, match="clinical escalation organization and contact"):
        settings.validate_deployment_safety()


def test_unsafe_staging_config_rejects_default_secret_and_http_cors():
    settings = safe_staging_settings(
        secret_key="change-me-in-production",
        cors_allowed_origins=["http://localhost:5173"],
    )

    with pytest.raises(RuntimeError, match="Unsafe deployment configuration"):
        settings.validate_deployment_safety()


def test_test_environment_allows_local_http_cors():
    settings = Settings(
        app_env="test",
        secret_key="test-secret-key-for-pytest-only-1234567890",
        cors_allowed_origins=["http://localhost:5173"],
        require_auth_for_analysis=False,
        enable_public_demo_mode=True,
    )

    settings.validate_deployment_safety()
    assert settings.effective_cors_origins == ["http://localhost:5173"]


def test_development_environment_allows_local_http_cors():
    settings = Settings(
        app_env="development",
        cors_allowed_origins=["http://localhost:5173"],
    )

    settings.validate_deployment_safety()
    assert settings.effective_cors_origins == ["http://localhost:5173"]


@pytest.mark.parametrize(
    "override",
    [
        {"secret_key": "change-me-in-production"},
        {"cors_allowed_origins": ["*"]},
        {"cors_allowed_origins": ["http://staging-web.example.test"]},
        {"require_auth_for_analysis": False},
        {"enable_public_demo_mode": True},
    ],
)
def test_staging_config_fails_closed(override):
    with pytest.raises(RuntimeError, match="Unsafe deployment configuration"):
        safe_staging_settings(**override).validate_deployment_safety()


def test_staging_cors_filters_wildcard():
    settings = safe_staging_settings(cors_allowed_origins=["*", "https://staging.example.com"])
    assert settings.effective_cors_origins == ["https://staging.example.com"]


def test_postgres_provider_urls_use_psycopg3():
    assert normalize_database_url("postgresql://user:pass@host/db") == "postgresql+psycopg://user:pass@host/db"
    assert normalize_database_url("postgres://user:pass@host/db") == "postgresql+psycopg://user:pass@host/db"
    assert normalize_database_url("sqlite:///local.db") == "sqlite:///local.db"


def test_database_url_can_be_built_from_secret_injected_fields(monkeypatch):
    monkeypatch.delenv("DATABASE_URL", raising=False)
    monkeypatch.setenv("DATABASE_HOST", "db.internal")
    monkeypatch.setenv("DATABASE_PORT", "5432")
    monkeypatch.setenv("DATABASE_NAME", "physiovision")
    monkeypatch.setenv("DATABASE_USER", "app_user")
    monkeypatch.setenv("DATABASE_PASSWORD", "p@ss:/word")

    assert database_url_from_environment() == "postgresql+psycopg://app_user:p%40ss%3A%2Fword@db.internal:5432/physiovision"


def test_protected_artifact_url_is_signed_and_rejects_unsigned_access(monkeypatch):
    settings = get_settings()
    monkeypatch.setattr(settings, "require_auth_for_analysis", True)
    monkeypatch.setattr(settings, "secret_key", "staging-only-secret-that-is-longer-than-32-characters")
    artifact_id = uuid4().hex
    url = build_artifact_url(f"/api/v1/artifacts/reports/{artifact_id}", artifact_id, "report")
    query = parse_qs(urlparse(url).query)
    expires, signature = int(query["expires"][0]), query["signature"][0]

    authorize_artifact(artifact_id, "report", None, expires, signature)
    with pytest.raises(AuthError) as exc:
        authorize_artifact(artifact_id, "report", None, None, None)
    assert exc.value.error_code == "AUTH_REQUIRED"


def test_signed_artifact_route_serves_only_authorized_link(monkeypatch, tmp_path):
    settings = get_settings()
    monkeypatch.setattr(settings, "require_auth_for_analysis", True)
    monkeypatch.setattr(settings, "secret_key", "staging-only-secret-that-is-longer-than-32-characters")
    monkeypatch.setattr(settings, "artifact_dir", tmp_path)
    artifact_id = uuid4().hex
    report = tmp_path / "reports" / f"{artifact_id}.pdf"
    report.parent.mkdir(parents=True)
    report.write_bytes(b"%PDF-1.4 staging test")
    plain = f"/api/v1/artifacts/reports/{artifact_id}"
    signed = build_artifact_url(plain, artifact_id, "report")
    client = TestClient(app)

    assert client.get(signed).status_code == 200
    response = client.get(plain)
    assert response.status_code == 401
    assert response.json()["error_code"] == "AUTH_REQUIRED"
