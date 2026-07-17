"""Standard API error contract."""

from pydantic import BaseModel, Field


class ErrorResponse(BaseModel):
    status: str = "error"
    error_code: str
    message: str
    details: list[str] = Field(default_factory=list)
