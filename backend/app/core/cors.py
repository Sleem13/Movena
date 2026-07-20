"""Shared CORS middleware options for browser and authenticated upload requests."""

from __future__ import annotations

from app.core.config import Settings


def cors_middleware_options(settings: Settings) -> dict[str, object]:
    """Build the FastAPI CORS options from the validated origin allowlist."""
    return {
        "allow_origins": settings.effective_cors_origins,
        "allow_credentials": True,
        "allow_methods": ["*"],
        "allow_headers": ["*"],
    }
