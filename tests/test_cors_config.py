from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.testclient import TestClient

from backend.app.core.config import Settings
from backend.app.core.cors import cors_middleware_options


RENDER_ORIGIN = "https://name-physiovision-api-staging.onrender.com"
VERCEL_ORIGIN = "https://physio-vision-ai.vercel.app"


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


def test_vercel_staging_origin_passes_authenticated_upload_preflight():
    settings = Settings(
        app_env="staging",
        secret_key="staging-only-secret-that-is-longer-than-32-characters",
        cors_allowed_origins=[RENDER_ORIGIN, VERCEL_ORIGIN],
        require_auth_for_analysis=True,
        enable_public_demo_mode=False,
        email_delivery_mode="smtp",
        smtp_host="smtp.example.com",
        email_from="no-reply@example.com",
        frontend_url="https://app.example.com",
    )
    settings.validate_deployment_safety()

    test_app = FastAPI()
    test_app.add_middleware(CORSMiddleware, **cors_middleware_options(settings))

    @test_app.post("/api/v1/analyze/squat")
    def analyze_upload():
        return {"status": "ok"}

    response = TestClient(test_app).options(
        "/api/v1/analyze/squat",
        headers={
            "Origin": VERCEL_ORIGIN,
            "Access-Control-Request-Method": "POST",
            "Access-Control-Request-Headers": "authorization,content-type,accept",
        },
    )

    assert response.status_code == 200
    assert response.headers["access-control-allow-origin"] == VERCEL_ORIGIN
    assert response.headers["access-control-allow-credentials"] == "true"
    assert "POST" in response.headers["access-control-allow-methods"]
    allowed_headers = response.headers["access-control-allow-headers"].lower()
    assert all(name in allowed_headers for name in ("authorization", "content-type", "accept"))
