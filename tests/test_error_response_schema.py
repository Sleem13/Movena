from backend.app.schemas.error_schema import ErrorResponse


def test_standard_error_response_shape():
    assert ErrorResponse(error_code="EMPTY_FILE", message="Empty.").model_dump() == {
        "status": "error", "error_code": "EMPTY_FILE", "message": "Empty.", "details": []
    }
