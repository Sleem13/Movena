"""Suggestion-only exercise-recognition candidate endpoints."""

from __future__ import annotations

from fastapi import APIRouter, Depends, File, Query, UploadFile, status
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.api.dependencies.auth import optional_current_user
from app.db.database import get_db
from app.db.models import User
from app.exercises.metadata import get_exercise_metadata

from app.services.exercise_recognition_service import (
    LIMITATIONS,
    SUPPORTED_TRACKS,
    list_available_recognition_models,
    predict_exercise_from_features,
    predict_exercise_from_sequence,
)
from app.ml.exercise_pose_features import extract_mediapipe_sequence_features
from app.services.pose_estimation_service import PoseEstimationError, extract_pose_landmarks
from app.utils.file_utils import UploadValidationError, remove_file, save_upload_file
from app.services.recognition_event_service import confirm_recognition_event, save_recognition_event


router = APIRouter(prefix="/api/v1/recognition", tags=["experimental-recognition"])


class RecognitionFeatureRequest(BaseModel):
    features: dict[str, float] = Field(default_factory=dict)
    sequence: list[dict[str, float]] = Field(default_factory=list)
    model_id: str | None = None


class RecognitionConfirmationRequest(BaseModel):
    event_id: str = Field(min_length=36, max_length=36)
    confirmed_exercise_id: str = Field(min_length=1, max_length=64)


def _record_result(
    result: dict[str, object],
    *,
    source_type: str,
    db: Session,
    actor_user_id: str | None,
    usable_pose_frames: int | None = None,
) -> dict[str, object]:
    try:
        row = save_recognition_event(
            result,
            source_type=source_type,
            usable_pose_frames=usable_pose_frames,
            actor_user_id=actor_user_id,
            db=db,
        )
    except SQLAlchemyError:
        result["audit_status"] = "failed"
        return result
    result["audit_status"] = "saved" if row else "not_applicable"
    if row:
        result["recognition_event_id"] = row.event_id
    return result


@router.get("/models")
def recognition_models() -> dict[str, object]:
    models = list_available_recognition_models()
    return {
        "status": "available" if models else "not_available",
        "experimental": True,
        "models": models,
        "supported_tracks": SUPPORTED_TRACKS,
        "limitations": LIMITATIONS,
    }


@router.post("/exercise")
def recognize_exercise(
    payload: RecognitionFeatureRequest,
    db: Session = Depends(get_db),
    current_user: User | None = Depends(optional_current_user),
) -> dict[str, object]:
    """Suggest an exercise from precomputed features; never run an analyzer."""

    if payload.sequence:
        return _record_result(
            predict_exercise_from_sequence(payload.sequence, payload.model_id),
            source_type="prepared_sequence",
            usable_pose_frames=len(payload.sequence),
            actor_user_id=current_user.user_id if current_user else None,
            db=db,
        )
    if not payload.features:
        return {
            "status": "not_implemented",
            "experimental": True,
            "message": "Upload-to-recognition feature extraction is not enabled. Submit a supported feature payload.",
            "limitations": LIMITATIONS,
        }
    return _record_result(
        predict_exercise_from_features(payload.features, payload.model_id),
        source_type="prepared_features",
        actor_user_id=current_user.user_id if current_user else None,
        db=db,
    )


@router.post("/video", response_model=None)
async def recognize_exercise_video(
    video: UploadFile = File(...),
    model_id: str | None = Query(None),
    db: Session = Depends(get_db),
    current_user: User | None = Depends(optional_current_user),
):
    """Suggest an exercise from an uploaded video using the temporal candidate."""

    try:
        video_path = await save_upload_file(video)
    except UploadValidationError as exc:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"status": "invalid_upload", "error_code": exc.error_code, "message": exc.message},
        )
    try:
        frames = extract_pose_landmarks(video_path)
        sequence = extract_mediapipe_sequence_features(frames)
        if not sequence:
            return JSONResponse(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                content={"status": "invalid_features", "message": "No compatible pose sequence was detected."},
            )
        result = predict_exercise_from_sequence(sequence, model_id)
        result["usable_pose_frames"] = len(sequence)
        return _record_result(
            result,
            source_type="video_upload",
            usable_pose_frames=len(sequence),
            actor_user_id=current_user.user_id if current_user else None,
            db=db,
        )
    except PoseEstimationError as exc:
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content={
                "status": "pose_error",
                "error_code": getattr(exc, "error_code", None) or "POSE_ERROR",
                "message": str(exc),
                "details": list(getattr(exc, "details", []) or []),
            },
        )
    finally:
        remove_file(video_path)


@router.post("/confirm")
def confirm_recognition(
    payload: RecognitionConfirmationRequest,
    db: Session = Depends(get_db),
    current_user: User | None = Depends(optional_current_user),
):
    """Record the user's label confirmation; no video or pose data is stored."""

    if get_exercise_metadata(payload.confirmed_exercise_id) is None:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"status": "invalid_confirmation", "message": "Unknown exercise label."},
        )
    row = confirm_recognition_event(
        payload.event_id,
        payload.confirmed_exercise_id,
        actor_user_id=current_user.user_id if current_user else None,
        db=db,
    )
    if row is None:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"status": "not_found", "message": "Recognition event was not found."},
        )
    return {
        "status": "confirmed",
        "recognition_event_id": row.event_id,
        "predicted_exercise_id": row.predicted_exercise_id,
        "confirmed_exercise_id": row.confirmed_exercise_id,
        "model_id": row.model_id,
    }
