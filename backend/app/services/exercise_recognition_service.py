"""Safe optional interface for experimental exercise-recognition models."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import joblib
import numpy as np


PROJECT_ROOT = Path(__file__).resolve().parents[3]
RECOGNITION_MODELS_DIR = PROJECT_ROOT / "models" / "recognition"
SUPPORTED_ANALYZERS = {"bodyweight_squat", "sit_to_stand"}
SUPPORTED_TRACKS = [
    "video_pose_recognition", "skeleton_sequence_recognition",
    "sensor_timeseries_recognition", "tabular_feature_recognition",
]
LIMITATIONS = [
    "Exercise recognition is experimental.",
    "Manual exercise selection remains primary.",
    "A suggestion does not provide clinical feedback or activate an unsupported analyzer.",
]


def _not_available(message: str = "No exercise recognition model is available yet.") -> dict[str, object]:
    return {"status": "not_available", "experimental": True, "message": message, "limitations": LIMITATIONS}


def list_available_recognition_models() -> list[dict[str, object]]:
    if not RECOGNITION_MODELS_DIR.is_dir():
        return []
    models: list[dict[str, object]] = []
    for directory in sorted(path for path in RECOGNITION_MODELS_DIR.iterdir() if path.is_dir()):
        metadata_path = directory / "metadata.json"
        artifact_path = directory / "model.joblib"
        if not metadata_path.is_file() or not artifact_path.is_file():
            continue
        try:
            metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            continue
        models.append({
            "model_id": metadata.get("model_id", directory.name),
            "model_name": metadata.get("model_name", "unknown"),
            "track": metadata.get("track", "unknown"),
            "classes": metadata.get("classes", []),
            "status": "experimental",
            "promoted_to_app": False,
        })
    return models


def load_recognition_model(model_id: str | None = None) -> dict[str, Any] | None:
    available = list_available_recognition_models()
    if not available:
        return None
    selected = next((model for model in available if model["model_id"] == model_id), None) if model_id else available[-1]
    if selected is None:
        return None
    directory = RECOGNITION_MODELS_DIR / str(selected["model_id"])
    try:
        metadata = json.loads((directory / "metadata.json").read_text(encoding="utf-8"))
        estimator = joblib.load(directory / "model.joblib")
    except (OSError, ValueError, json.JSONDecodeError):
        return None
    return {"estimator": estimator, "metadata": metadata}


def format_recognition_result(prediction: dict[str, object]) -> dict[str, object]:
    if prediction.get("status") != "success":
        result = dict(prediction)
        result.setdefault("experimental", True)
        result.setdefault("limitations", LIMITATIONS)
        return result
    suggested = str(prediction["suggested_exercise_id"])
    confidence = float(prediction.get("confidence", 0.0))
    return {
        "status": "success",
        "experimental": True,
        "suggested_exercise_id": suggested,
        "confidence": confidence,
        "top_predictions": prediction.get("top_predictions", []),
        "analyzer_available": suggested in SUPPORTED_ANALYZERS,
        "requires_manual_confirmation": True,
        "can_auto_route": False,
        "limitations": LIMITATIONS,
    }


def predict_exercise_from_features(features: dict[str, float], model_id: str | None = None) -> dict[str, object]:
    bundle = load_recognition_model(model_id)
    if bundle is None:
        return _not_available()
    metadata = bundle["metadata"]
    feature_columns = list(metadata.get("feature_columns", []))
    missing = [column for column in feature_columns if column not in features]
    if missing:
        return format_recognition_result({
            "status": "invalid_features",
            "message": f"Required recognition features are missing: {', '.join(missing[:10])}",
        })
    values = np.asarray([[float(features[column]) for column in feature_columns]], dtype=float)
    estimator = bundle["estimator"]
    try:
        probabilities = estimator.predict_proba(values)[0]
        classes = list(estimator.classes_)
    except (AttributeError, ValueError, TypeError) as exc:
        return format_recognition_result({"status": "not_available", "message": f"Recognition inference is unavailable: {exc}"})
    ranked = sorted(
        ({"exercise_id": str(label), "confidence": round(float(score), 6)} for label, score in zip(classes, probabilities)),
        key=lambda item: item["confidence"], reverse=True,
    )
    return format_recognition_result({
        "status": "success",
        "suggested_exercise_id": ranked[0]["exercise_id"],
        "confidence": ranked[0]["confidence"],
        "top_predictions": ranked[:3],
    })

