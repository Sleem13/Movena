from functools import lru_cache
from pathlib import Path

from pydantic import BaseModel


class Settings(BaseModel):
    project_name: str = "PhysioVision AI"
    version: str = "0.1.0"
    api_v1_prefix: str = "/api/v1"
    upload_dir: Path = Path("tmp/uploads")
    min_landmark_visibility: float = 0.45
    allowed_video_extensions: set[str] = {".mp4", ".mov", ".avi", ".mkv", ".webm"}


@lru_cache
def get_settings() -> Settings:
    return Settings()
