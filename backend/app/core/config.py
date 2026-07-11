from functools import lru_cache
from pathlib import Path

from pydantic import BaseModel


class Settings(BaseModel):
    project_name: str = "PhysioVision AI"
    version: str = "0.1.0"
    api_v1_prefix: str = "/api/v1"
    upload_dir: Path = Path("tmp/uploads")
    artifact_dir: Path = Path("tmp/artifacts")
    artifact_ttl_seconds: int = 60 * 60
    max_frame_analysis_rows: int = 300
    max_upload_size_bytes: int = 100 * 1024 * 1024
    min_readable_video_frames: int = 3
    min_landmark_visibility: float = 0.45
    allowed_video_extensions: set[str] = {".mp4", ".mov", ".avi", ".mkv", ".webm"}
    allowed_video_mime_types: set[str] = {
        "video/mp4",
        "video/quicktime",
        "video/x-msvideo",
        "video/x-matroska",
        "video/webm",
        "application/octet-stream",
    }


@lru_cache
def get_settings() -> Settings:
    return Settings()
