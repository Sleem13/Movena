from backend.app.core.config import DEFAULT_CORS_ORIGINS, Settings


def test_config_loads_safe_defaults(monkeypatch):
    for name in ("APP_ENV", "APP_VERSION", "CORS_ALLOWED_ORIGINS", "MAX_UPLOAD_SIZE_MB", "ARTIFACT_RETENTION_HOURS"):
        monkeypatch.delenv(name, raising=False)
    settings = Settings.from_environment()
    assert settings.app_env == "development"
    assert settings.version == "0.12.0"
    assert settings.max_upload_size_mb == 100
    assert settings.artifact_retention_hours == 24
    assert settings.cors_allowed_origins == DEFAULT_CORS_ORIGINS


def test_config_parses_origins_and_blocks_production_wildcard(monkeypatch):
    monkeypatch.setenv("APP_ENV", "production")
    monkeypatch.setenv("CORS_ALLOWED_ORIGINS", "*,https://app.example.com")
    settings = Settings.from_environment()
    assert settings.effective_cors_origins == ["https://app.example.com"]


def test_config_reads_app_version(monkeypatch):
    monkeypatch.setenv("APP_VERSION", "0.12.9-test")
    assert Settings.from_environment().version == "0.12.9-test"
