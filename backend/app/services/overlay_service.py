"""Backward-compatible imports for the renamed overlay video service."""

from app.services.overlay_video_service import (  # noqa: F401
    OverlayArtifact,
    OverlayGenerationError,
    create_overlay_video,
    generate_skeleton_overlay,
)
