from pathlib import Path
from uuid import uuid4

from fastapi import UploadFile

from app.core.config import get_settings


class UploadValidationError(ValueError):
    def __init__(self, error_code: str, message: str):
        super().__init__(message)
        self.error_code = error_code
        self.message = message


def validate_video_file(file: UploadFile) -> None:
    settings = get_settings()
    suffix = Path(file.filename or "").suffix.lower()
    if suffix not in settings.allowed_video_extensions:
        allowed = ", ".join(sorted(settings.allowed_video_extensions))
        raise UploadValidationError(
            "INVALID_FILE_TYPE",
            f"Only supported video files are accepted: {allowed}.",
        )
    if file.content_type and file.content_type.lower() not in settings.allowed_video_mime_types:
        raise UploadValidationError(
            "INVALID_FILE_TYPE",
            "The upload MIME type does not match a supported video format.",
        )


async def save_upload_file(file: UploadFile) -> Path:
    validate_video_file(file)
    settings = get_settings()
    settings.upload_dir.mkdir(parents=True, exist_ok=True)
    suffix = Path(file.filename or "video.mp4").suffix.lower()
    destination = settings.upload_dir / f"{uuid4().hex}{suffix}"

    total_bytes = 0
    with destination.open("wb") as buffer:
        while chunk := await file.read(1024 * 1024):
            total_bytes += len(chunk)
            if total_bytes > settings.max_upload_size_bytes:
                buffer.close()
                destination.unlink(missing_ok=True)
                raise UploadValidationError(
                    "FILE_TOO_LARGE",
                    f"Video exceeds the {settings.max_upload_size_bytes // (1024 * 1024)} MB limit.",
                )
            buffer.write(chunk)

    if total_bytes == 0:
        destination.unlink(missing_ok=True)
        raise UploadValidationError("EMPTY_FILE", "Uploaded video is empty.")

    return destination


def remove_file(path: Path) -> None:
    path.unlink(missing_ok=True)
