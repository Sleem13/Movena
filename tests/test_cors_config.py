from backend.app.core.config import Settings


def test_cors_origins_parse_cleanly(monkeypatch):
    monkeypatch.setenv("CORS_ALLOWED_ORIGINS", "http://localhost:5173, https://mobile.example")
    assert Settings.from_environment().cors_allowed_origins == [
        "http://localhost:5173", "https://mobile.example"
    ]


def test_default_development_cors_supports_expo_web():
    settings = Settings()
    assert "http://localhost:8081" in settings.effective_cors_origins
    assert "http://127.0.0.1:8081" in settings.effective_cors_origins


def test_production_cors_never_returns_wildcard():
    settings = Settings(app_env="production", cors_allowed_origins=["*", "https://app.example"])
    assert settings.effective_cors_origins == ["https://app.example"]


def test_mobile_upload_limit_is_environment_configurable(monkeypatch):
    monkeypatch.setenv("MAX_UPLOAD_SIZE_MB", "75")
    settings = Settings.from_environment()
    assert settings.max_upload_size_mb == 75
    assert settings.max_upload_size_bytes == 75 * 1024 * 1024
