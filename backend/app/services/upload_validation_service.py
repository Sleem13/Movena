"""Central video upload metadata and streaming-size validation."""

from __future__ import annotations

from pathlib import Path

from fastapi import UploadFile

from app.core.config import Settings, get_settings


class UploadValidationError(ValueError):
    def __init__(self, error_code: str, message: str):
        super().__init__(message)
        self.error_code = error_code
        self.message = message


def validate_filename(filename: str | None) -> str:
    value = (filename or "").strip()
    if (
        not value or "\x00" in value or "/" in value or "\\" in value
        or value in {".", ".."} or Path(value).name != value
    ):
        raise UploadValidationError("INVALID_FILENAME", "Uploaded filename is invalid or unsafe.")
    return value


def validate_upload_metadata(file: UploadFile | None, settings: Settings | None = None) -> None:
    config = settings or get_settings()
    if file is None or file.file is None:
        raise UploadValidationError("MISSING_FILE", "A video file is required.")
    filename = validate_filename(file.filename)
    suffix = Path(filename).suffix.lower()
    if suffix not in config.allowed_video_extensions:
        allowed = ", ".join(sorted(config.allowed_video_extensions))
        raise UploadValidationError(
            "UNSUPPORTED_FILE_TYPE", f"Only supported video files are accepted: {allowed}.",
        )
    if file.content_type and file.content_type.lower() not in config.allowed_video_mime_types:
        raise UploadValidationError(
            "UNSUPPORTED_FILE_TYPE", "The upload content type is not a supported video format.",
        )


def validate_stream_size(total_bytes: int, settings: Settings | None = None) -> None:
    config = settings or get_settings()
    if total_bytes <= 0:
        raise UploadValidationError("EMPTY_FILE", "Uploaded video is empty.")
    if total_bytes > config.max_upload_size_bytes:
        raise UploadValidationError(
            "FILE_TOO_LARGE", "Uploaded file exceeds the maximum allowed size.",
        )
