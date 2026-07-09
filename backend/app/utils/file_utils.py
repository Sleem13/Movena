from pathlib import Path
from uuid import uuid4

from fastapi import HTTPException, UploadFile, status

from app.core.config import get_settings


def validate_video_file(file: UploadFile) -> None:
    settings = get_settings()
    suffix = Path(file.filename or "").suffix.lower()
    if suffix not in settings.allowed_video_extensions:
        allowed = ", ".join(sorted(settings.allowed_video_extensions))
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid file type. Upload one of: {allowed}.",
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
            buffer.write(chunk)

    if total_bytes == 0:
        destination.unlink(missing_ok=True)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Uploaded video is empty.",
        )

    return destination


def remove_file(path: Path) -> None:
    path.unlink(missing_ok=True)
