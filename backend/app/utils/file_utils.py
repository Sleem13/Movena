from pathlib import Path
from uuid import uuid4

from fastapi import UploadFile

from app.core.config import get_settings
from app.services.upload_validation_service import (
    UploadValidationError, validate_stream_size, validate_upload_metadata,
)


def validate_video_file(file: UploadFile) -> None:
    """Compatibility wrapper for existing route imports and tests."""
    validate_upload_metadata(file)


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
                raise UploadValidationError("FILE_TOO_LARGE", "Uploaded file exceeds the maximum allowed size.")
            buffer.write(chunk)

    try:
        validate_stream_size(total_bytes, settings)
    except UploadValidationError:
        destination.unlink(missing_ok=True)
        raise

    return destination


def remove_file(path: Path) -> None:
    path.unlink(missing_ok=True)
