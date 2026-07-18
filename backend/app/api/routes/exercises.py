"""Read-only exercise catalog for web and future mobile clients."""

from fastapi import APIRouter, status
from fastapi.responses import JSONResponse

from app.exercises.metadata import ExerciseMetadata, get_exercise_metadata, list_exercise_metadata
from app.schemas.error_schema import ErrorResponse

router = APIRouter(prefix="/api/v1/exercises", tags=["exercises"])


@router.get("", response_model=list[ExerciseMetadata])
def exercises() -> tuple[ExerciseMetadata, ...]:
    return list_exercise_metadata()


@router.get("/{exercise_id}", response_model=ExerciseMetadata, responses={404: {"model": ErrorResponse}})
def exercise_detail(exercise_id: str) -> ExerciseMetadata | JSONResponse:
    item = get_exercise_metadata(exercise_id)
    if item is not None:
        return item
    payload = ErrorResponse(
        error_code="EXERCISE_NOT_FOUND",
        message="Exercise metadata was not found.",
        details=["Use GET /api/v1/exercises to view supported and planned exercises."],
    )
    return JSONResponse(status_code=status.HTTP_404_NOT_FOUND, content=payload.model_dump())
