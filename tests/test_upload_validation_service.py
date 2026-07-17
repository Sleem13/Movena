from io import BytesIO

import pytest
from fastapi import UploadFile

from backend.app.core.config import Settings
from backend.app.services.upload_validation_service import (
    UploadValidationError, validate_stream_size, validate_upload_metadata,
)


def upload(name="clip.mp4", content_type="video/mp4"):
    return UploadFile(filename=name, file=BytesIO(b"video"), headers={"content-type": content_type})


@pytest.mark.parametrize("name,code", [("clip.exe", "UNSUPPORTED_FILE_TYPE"), ("../clip.mp4", "INVALID_FILENAME")])
def test_upload_metadata_rejections(name, code):
    with pytest.raises(UploadValidationError) as exc:
        validate_upload_metadata(upload(name))
    assert exc.value.error_code == code


def test_empty_and_too_large_rejections():
    settings = Settings(max_upload_size_bytes=4)
    with pytest.raises(UploadValidationError, match="empty"):
        validate_stream_size(0, settings)
    with pytest.raises(UploadValidationError) as exc:
        validate_stream_size(5, settings)
    assert exc.value.error_code == "FILE_TOO_LARGE"


def test_missing_upload_rejection():
    with pytest.raises(UploadValidationError) as exc:
        validate_upload_metadata(None)
    assert exc.value.error_code == "MISSING_FILE"
