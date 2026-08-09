"""Suggestion-only exercise-recognition candidate endpoints."""

from __future__ import annotations

from fastapi import APIRouter, File, Query, UploadFile, status
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

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


router = APIRouter(prefix="/api/v1/recognition", tags=["experimental-recognition"])


class RecognitionFeatureRequest(BaseModel):
    features: dict[str, float] = Field(default_factory=dict)
    sequence: list[dict[str, float]] = Field(default_factory=list)
    model_id: str | None = None


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
def recognize_exercise(payload: RecognitionFeatureRequest) -> dict[str, object]:
    """Suggest an exercise from precomputed features; never run an analyzer."""

    if payload.sequence:
        return predict_exercise_from_sequence(payload.sequence, payload.model_id)
    if not payload.features:
        return {
            "status": "not_implemented",
            "experimental": True,
            "message": "Upload-to-recognition feature extraction is not enabled. Submit a supported feature payload.",
            "limitations": LIMITATIONS,
        }
    return predict_exercise_from_features(payload.features, payload.model_id)


@router.post("/video", response_model=None)
async def recognize_exercise_video(
    video: UploadFile = File(...),
    model_id: str | None = Query(None),
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
        return result
    except PoseEstimationError as exc:
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content={"status": "pose_error", "message": str(exc)},
        )
    finally:
        remove_file(video_path)
