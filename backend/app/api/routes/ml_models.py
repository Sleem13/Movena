from fastapi import APIRouter

from app.core.config import get_settings
from app.services.ml_model_readiness_service import ml_model_readiness


router = APIRouter(prefix="/api/v1/ml", tags=["ml"])


@router.get("/readiness")
def model_readiness() -> dict:
    settings = get_settings()
    return {
        "feature_enabled": settings.enable_ml_second_opinion,
        **ml_model_readiness(),
    }
