"""Experimental suggestion-only exercise-recognition endpoints."""

from __future__ import annotations

from fastapi import APIRouter
from pydantic import BaseModel, Field

from app.services.exercise_recognition_service import (
    LIMITATIONS,
    SUPPORTED_TRACKS,
    list_available_recognition_models,
    predict_exercise_from_features,
)


router = APIRouter(prefix="/api/v1/recognition", tags=["experimental-recognition"])


class RecognitionFeatureRequest(BaseModel):
    features: dict[str, float] = Field(default_factory=dict)
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

    if not payload.features:
        return {
            "status": "not_implemented",
            "experimental": True,
            "message": "Upload-to-recognition feature extraction is not enabled. Submit a supported feature payload.",
            "limitations": LIMITATIONS,
        }
    return predict_exercise_from_features(payload.features, payload.model_id)

