"""Safe optional interface for exercise-recognition model candidates."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import joblib
import numpy as np

from app.exercises.registry import registry


PROJECT_ROOT = Path(__file__).resolve().parents[3]
RECOGNITION_MODELS_DIR = PROJECT_ROOT / "models" / "recognition"
SUPPORTED_TRACKS = [
    "video_pose_recognition", "skeleton_sequence_recognition",
    "sensor_timeseries_recognition", "tabular_feature_recognition",
]
LIMITATIONS = [
    "Exercise recognition is a development candidate.",
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
        if not metadata_path.is_file():
            continue
        try:
            metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            continue
        artifact_format = metadata.get("artifact_format", "joblib")
        artifact_name = {
            "xgboost_json": "model.json",
            "torchscript_sequence": "model.pt",
        }.get(artifact_format, "model.joblib")
        if not (directory / artifact_name).is_file():
            continue
        models.append({
            "model_id": metadata.get("model_id", directory.name),
            "model_name": metadata.get("model_name", "unknown"),
            "track": metadata.get("track", "unknown"),
            "classes": metadata.get("classes", []),
            "artifact_format": artifact_format,
            "status": metadata.get("status", "experimental"),
            "promoted_to_app": bool(metadata.get("promoted_to_app", False)),
        })
    return models


def load_recognition_model(
    model_id: str | None = None, *, required_format: str | None = None
) -> dict[str, Any] | None:
    available = list_available_recognition_models()
    if required_format and model_id is None:
        available = [model for model in available if model["artifact_format"] == required_format]
    if not available:
        return None
    selected = next((model for model in available if model["model_id"] == model_id), None) if model_id else available[-1]
    if selected is None:
        return None
    directory = RECOGNITION_MODELS_DIR / str(selected["model_id"])
    try:
        metadata = json.loads((directory / "metadata.json").read_text(encoding="utf-8"))
        artifact_format = metadata.get("artifact_format", "joblib")
        if artifact_format == "xgboost_json":
            from xgboost import XGBClassifier
            estimator = XGBClassifier()
            estimator.load_model(directory / "model.json")
        elif artifact_format == "torchscript_sequence":
            import torch
            estimator = torch.jit.load(str(directory / "model.pt"), map_location="cpu")
            estimator.eval()
        else:
            estimator = joblib.load(directory / "model.joblib")
    except (ImportError, OSError, ValueError, json.JSONDecodeError):
        return None
    return {"estimator": estimator, "metadata": metadata}


def format_recognition_result(prediction: dict[str, object]) -> dict[str, object]:
    status = str(prediction.get("status", "not_available"))
    if status not in {"success", "uncertain"}:
        result = dict(prediction)
        result.setdefault("experimental", True)
        result.setdefault("limitations", LIMITATIONS)
        return result
    suggested = str(prediction["suggested_exercise_id"])
    confidence = float(prediction.get("confidence", 0.0))
    analyzer_available = suggested in registry.available_exercises()
    return {
        "status": status,
        "experimental": True,
        "suggested_exercise_id": suggested,
        "confidence": confidence,
        "top_predictions": prediction.get("top_predictions", []),
        "analyzer_available": analyzer_available,
        "requires_manual_confirmation": True,
        "suggestion_actionable": status == "success" and analyzer_available,
        "can_auto_route": False,
        "confidence_threshold": prediction.get("confidence_threshold"),
        "message": prediction.get("message"),
        "limitations": LIMITATIONS,
    }


def predict_exercise_from_features(features: dict[str, float], model_id: str | None = None) -> dict[str, object]:
    bundle = load_recognition_model(model_id, required_format="xgboost_json")
    if bundle is None:
        return _not_available()
    metadata = bundle["metadata"]
    if metadata.get("artifact_format") == "torchscript_sequence":
        return format_recognition_result({
            "status": "invalid_features",
            "message": "The selected model requires a sequence of pose-feature frames.",
        })
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
        classes = list(metadata.get("classes", [])) or list(estimator.classes_)
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


def _resample_feature_sequence(values: np.ndarray, sequence_length: int) -> np.ndarray:
    if len(values) == 0:
        raise ValueError("At least one pose-feature frame is required.")
    if len(values) == 1:
        return np.repeat(values, sequence_length, axis=0)
    source = np.linspace(0.0, 1.0, len(values))
    target = np.linspace(0.0, 1.0, sequence_length)
    return np.stack(
        [np.interp(target, source, values[:, column]) for column in range(values.shape[1])],
        axis=1,
    )


def predict_exercise_from_sequence(
    sequence: list[dict[str, float]], model_id: str | None = None
) -> dict[str, object]:
    """Suggest an exercise from an ordered sequence of prepared pose features."""

    bundle = load_recognition_model(model_id, required_format="torchscript_sequence")
    if bundle is None:
        return _not_available()
    metadata = bundle["metadata"]
    if metadata.get("artifact_format") != "torchscript_sequence":
        return format_recognition_result({
            "status": "invalid_features",
            "message": "The selected model accepts a single pose-feature frame, not a sequence.",
        })
    if not sequence:
        return format_recognition_result({
            "status": "invalid_features", "message": "At least one pose-feature frame is required."
        })
    columns = list(metadata.get("feature_columns", []))
    missing = sorted({column for frame in sequence for column in columns if column not in frame})
    if missing:
        return format_recognition_result({
            "status": "invalid_features",
            "message": f"Required recognition features are missing: {', '.join(missing[:10])}",
        })
    try:
        import torch

        values = np.asarray(
            [[float(frame[column]) for column in columns] for frame in sequence], dtype=np.float32
        )
        if not np.isfinite(values).all():
            raise ValueError("Pose features must be finite numbers.")
        length = int(metadata["sequence_length"])
        values = _resample_feature_sequence(values, length)
        mean = np.asarray(metadata["feature_mean"], dtype=np.float32)
        std = np.asarray(metadata["feature_std"], dtype=np.float32)
        normalized = ((values - mean) / std).astype(np.float32)
        temperature = float(metadata.get("temperature", 1.0))
        if temperature <= 0:
            raise ValueError("Model calibration temperature must be positive.")
        with torch.no_grad():
            logits = bundle["estimator"](torch.from_numpy(normalized).unsqueeze(0))
            probabilities = torch.softmax(
                logits / temperature, dim=1
            )[0].numpy()
    except (ImportError, KeyError, TypeError, ValueError, RuntimeError) as exc:
        return format_recognition_result({
            "status": "not_available", "message": f"Sequence recognition inference is unavailable: {exc}"
        })
    classes = list(metadata.get("classes", []))
    ranked = sorted(
        ({"exercise_id": str(label), "confidence": round(float(score), 6)}
         for label, score in zip(classes, probabilities)),
        key=lambda item: item["confidence"],
        reverse=True,
    )
    confidence_threshold = float(metadata.get("confidence_threshold", 0.0))
    is_uncertain = ranked[0]["confidence"] < confidence_threshold
    return format_recognition_result({
        "status": "uncertain" if is_uncertain else "success",
        "suggested_exercise_id": ranked[0]["exercise_id"],
        "confidence": ranked[0]["confidence"],
        "top_predictions": ranked[:3],
        "confidence_threshold": confidence_threshold,
        "message": (
            "Confidence is below the calibrated threshold; choose the exercise manually."
            if is_uncertain else None
        ),
    })
