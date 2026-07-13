"""Optional experimental inference for the trusted Sprint 5 baseline artifact."""

from __future__ import annotations

import json
import logging
from pathlib import Path

from app.schemas.analysis_schema import MLPrediction
from app.services.ml_feature_adapter_service import aggregate_pose_frames


MODEL_VERSION = "sprint_5_baseline"
EXPERIMENTAL_WARNING = "Experimental baseline model. Not clinically validated."
UNAVAILABLE_WARNING = "ML baseline unavailable. Rule-based analysis is still available."
INVALID_SQUAT_WARNING = "ML prediction skipped because no valid squat movement was detected."
REPO_ROOT = Path(__file__).resolve().parents[3]
DEFAULT_MODEL_PATH = REPO_ROOT / "models/squat_baseline/artifacts/squat_quality_baseline.pkl"
DEFAULT_FEATURES_PATH = REPO_ROOT / "models/squat_baseline/feature_columns.json"
DEFAULT_LABELS_PATH = REPO_ROOT / "models/squat_baseline/label_mapping.json"
logger = logging.getLogger(__name__)


def unavailable_prediction(reason: str | None = None) -> MLPrediction:
    warning = UNAVAILABLE_WARNING if not reason else f"{UNAVAILABLE_WARNING} {reason}"
    return MLPrediction(enabled=False, model_version=MODEL_VERSION, warning=warning)


def invalid_squat_prediction() -> MLPrediction:
    return MLPrediction(
        enabled=False,
        model_version=MODEL_VERSION,
        warning=INVALID_SQUAT_WARNING,
        ml_confidence_level="not_applicable",
    )


def predict_experimental_quality(
    frames: list[dict],
    model_path: Path = DEFAULT_MODEL_PATH,
    features_path: Path = DEFAULT_FEATURES_PATH,
    labels_path: Path = DEFAULT_LABELS_PATH,
) -> MLPrediction:
    try:
        import joblib

        if not model_path.exists() or not features_path.exists() or not labels_path.exists():
            return unavailable_prediction("Required model artifacts are missing.")
        bundle = joblib.load(model_path)
        feature_columns = json.loads(features_path.read_text(encoding="utf-8"))
        label_mapping = json.loads(labels_path.read_text(encoding="utf-8"))
        if feature_columns != bundle.get("feature_columns"):
            return unavailable_prediction("Saved feature contracts do not match.")
        if label_mapping != bundle.get("label_mapping"):
            return unavailable_prediction("Saved label mappings do not match.")
        features = aggregate_pose_frames(frames, feature_columns)
        model = bundle["model"]
        predicted_label = str(model.predict(features)[0])
        probabilities = model.predict_proba(features) if hasattr(model, "predict_proba") else None
        confidence = float(probabilities[0].max()) if probabilities is not None else None
        return MLPrediction(
            enabled=True,
            predicted_label=predicted_label,
            confidence=confidence,
            model_name=str(bundle.get("model_name", "unknown_baseline")),
            model_version=str(bundle.get("model_version", MODEL_VERSION)),
            warning=EXPERIMENTAL_WARNING,
        )
    except Exception as exc:
        logger.warning("Experimental ML inference disabled: %s", exc)
        return unavailable_prediction("Inference could not be completed safely.")
