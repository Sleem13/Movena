"""Safe optional interface for exercise-recognition model candidates."""

from __future__ import annotations

import json
import hashlib
import logging
from functools import lru_cache
from pathlib import Path
from typing import Any

import joblib
import numpy as np

from app.exercises.registry import registry
from app.core.config import Settings, get_settings


PROJECT_ROOT = Path(__file__).resolve().parents[3]
RECOGNITION_MODELS_DIR = PROJECT_ROOT / "models" / "recognition"
SUPPORTED_TRACKS = [
    "video_pose_recognition", "skeleton_sequence_recognition",
    "sensor_timeseries_recognition", "tabular_feature_recognition",
]
LIMITATIONS = [
    "Exercise recognition provides an assisted suggestion that must be confirmed before analysis.",
    "Manual exercise selection remains primary.",
    "A suggestion does not provide clinical feedback or activate an unsupported analyzer.",
]
logger = logging.getLogger(__name__)
ACTIVE_RECOGNITION_MODEL_HEALTH: dict[str, dict[str, object]] = {}


def _artifact_name(artifact_format: str) -> str:
    return {"xgboost_json": "model.json", "torchscript_sequence": "model.pt"}.get(
        artifact_format, "model.joblib"
    )


def _configured_model_id(required_format: str | None, settings: Settings | None = None) -> str:
    configured = settings or get_settings()
    if required_format == "xgboost_json":
        return configured.active_frame_recognition_model_id
    return configured.active_sequence_recognition_model_id


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
        artifact_name = _artifact_name(artifact_format)
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
            "active": directory.name == _configured_model_id(artifact_format),
            "integrity_status": ACTIVE_RECOGNITION_MODEL_HEALTH.get(directory.name, {}).get(
                "status", "not_checked"
            ),
        })
    return models


def verify_recognition_artifact(model_id: str, *, smoke_inference: bool = True) -> dict[str, object]:
    """Validate an artifact's bytes, feature contract, calibration, and loadability."""

    directory = RECOGNITION_MODELS_DIR / model_id
    errors: list[str] = []
    try:
        metadata = json.loads((directory / "metadata.json").read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        return {"model_id": model_id, "status": "invalid", "valid": False, "errors": [str(exc)]}
    artifact_format = str(metadata.get("artifact_format", "joblib"))
    artifact_path = directory / _artifact_name(artifact_format)
    classes = list(metadata.get("classes", []))
    columns = list(metadata.get("feature_columns", []))
    if metadata.get("model_id") != model_id:
        errors.append("metadata model_id does not match its directory")
    if not classes or len(classes) != len(set(classes)):
        errors.append("classes must be non-empty and unique")
    if not columns or len(columns) != len(set(columns)):
        errors.append("feature columns must be non-empty and unique")
    if not artifact_path.is_file():
        errors.append(f"artifact file is missing: {artifact_path.name}")
    elif not metadata.get("artifact_sha256"):
        errors.append("artifact_sha256 is missing")
    elif hashlib.sha256(artifact_path.read_bytes()).hexdigest() != metadata["artifact_sha256"]:
        errors.append("artifact SHA-256 does not match metadata")
    if artifact_format == "torchscript_sequence":
        length = int(metadata.get("sequence_length", 0))
        mean = np.asarray(metadata.get("feature_mean", []), dtype=float)
        std = np.asarray(metadata.get("feature_std", []), dtype=float)
        temperature = float(metadata.get("temperature", 0.0))
        threshold = float(metadata.get("confidence_threshold", -1.0))
        if length < 2 or len(mean) != len(columns) or len(std) != len(columns):
            errors.append("sequence length or normalization vectors do not match the feature contract")
        if not np.isfinite(mean).all() or not np.isfinite(std).all() or (std <= 0).any():
            errors.append("normalization values must be finite with positive standard deviations")
        if temperature <= 0 or not 0 <= threshold <= 1:
            errors.append("calibration temperature or confidence threshold is invalid")
    if errors or not smoke_inference:
        return {
            "model_id": model_id,
            "artifact_format": artifact_format,
            "status": "valid" if not errors else "invalid",
            "valid": not errors,
            "errors": errors,
        }
    try:
        if artifact_format == "torchscript_sequence":
            import torch

            estimator = torch.jit.load(str(artifact_path), map_location="cpu")
            estimator.eval()
            sample = torch.zeros(1, int(metadata["sequence_length"]), len(columns), dtype=torch.float32)
            with torch.no_grad():
                output = estimator(sample)
            if tuple(output.shape) != (1, len(classes)) or not torch.isfinite(output).all():
                errors.append("TorchScript smoke output does not match the class contract")
        elif artifact_format == "xgboost_json":
            from xgboost import XGBClassifier

            estimator = XGBClassifier()
            estimator.load_model(artifact_path)
            probabilities = estimator.predict_proba(np.zeros((1, len(columns)), dtype=float))
            if probabilities.shape != (1, len(classes)) or not np.isfinite(probabilities).all():
                errors.append("XGBoost smoke output does not match the class contract")
        else:
            joblib.load(artifact_path)
    except (ImportError, OSError, RuntimeError, TypeError, ValueError) as exc:
        errors.append(f"artifact smoke inference failed: {exc}")
    return {
        "model_id": model_id,
        "artifact_format": artifact_format,
        "status": "valid" if not errors else "invalid",
        "valid": not errors,
        "errors": errors,
    }


def initialize_active_recognition_models(
    settings: Settings | None = None, *, strict: bool = False
) -> dict[str, dict[str, object]]:
    """Run startup integrity and inference checks for the two explicitly pinned artifacts."""

    configured = settings or get_settings()
    load_recognition_model.cache_clear()
    model_ids = {
        configured.active_sequence_recognition_model_id,
        configured.active_frame_recognition_model_id,
    }
    health = {model_id: verify_recognition_artifact(model_id) for model_id in model_ids if model_id}
    ACTIVE_RECOGNITION_MODEL_HEALTH.clear()
    ACTIVE_RECOGNITION_MODEL_HEALTH.update(health)
    invalid = [model_id for model_id, result in health.items() if not result["valid"]]
    if invalid:
        message = "Active recognition artifact verification failed: " + ", ".join(invalid)
        if strict:
            raise RuntimeError(message)
        logger.warning(message)
    for artifact_format in ("torchscript_sequence", "xgboost_json"):
        bundle = load_recognition_model(required_format=artifact_format)
        if bundle is not None:
            logger.info(
                "Preloaded recognition weights: model_id=%s format=%s",
                bundle["metadata"].get("model_id"),
                artifact_format,
            )
    return health


@lru_cache(maxsize=4)
def load_recognition_model(
    model_id: str | None = None, *, required_format: str | None = None
) -> dict[str, Any] | None:
    available = list_available_recognition_models()
    if required_format and model_id is None:
        available = [model for model in available if model["artifact_format"] == required_format]
    if not available:
        return None
    configured_id = _configured_model_id(required_format)
    if model_id is not None and model_id != configured_id:
        return None
    selected_id = configured_id
    selected = next((model for model in available if model["model_id"] == selected_id), None)
    if selected is None:
        return None
    directory = RECOGNITION_MODELS_DIR / str(selected["model_id"])
    try:
        metadata = json.loads((directory / "metadata.json").read_text(encoding="utf-8"))
        if not verify_recognition_artifact(str(selected["model_id"]), smoke_inference=False)["valid"]:
            return None
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
        "model_id": prediction.get("model_id"),
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
        "model_id": metadata.get("model_id"),
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
        "model_id": metadata.get("model_id"),
    })
