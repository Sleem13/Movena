from fastapi.responses import JSONResponse

from app.schemas.error_schema import ErrorResponse


def api_error_response(
    code: str,
    message: str,
    status_code: int = 400,
) -> JSONResponse:
    return JSONResponse(
        status_code=status_code,
        content=ErrorResponse(error_code=code, message=message).model_dump(),
    )
