"""Exercise-wide optional ML second-opinion orchestration.

The rule-based analyzers remain the source of truth. This service only adds a
request-scoped, experimental model result when a compatible provider exists.
"""

from __future__ import annotations

import importlib
import json
import logging
import os
from pathlib import Path
from typing import Any

from app.exercises.registry import registry
from app.schemas.analysis_schema import AnalysisResponse, MLPrediction
from app.services.analysis_confidence_service import apply_ml_confidence_context, enrich_ml_prediction
from app.services.ml_prediction_service import (
    INVALID_SQUAT_WARNING,
    MODEL_VERSION,
    invalid_squat_prediction,
    predict_experimental_quality,
)


logger = logging.getLogger(__name__)

MODEL_MODE_CLASSICAL_POSE_BASELINE = "classical_pose_baseline"
MODEL_MODE_PRETRAINED_AS_IS = "pretrained_as_is"
MODEL_MODE_FINE_TUNED = "fine_tuned"
MODEL_MODE_FEATURE_EXTRACTOR = "feature_extractor"
SUPPORTED_MODEL_MODES = (
    MODEL_MODE_CLASSICAL_POSE_BASELINE,
    MODEL_MODE_PRETRAINED_AS_IS,
    MODEL_MODE_FINE_TUNED,
    MODEL_MODE_FEATURE_EXTRACTOR,
)
DEFAULT_FEATURE_SOURCE = "pose_landmarks"
DISABLED_DEPLOYMENT_WARNING = "ML second opinion is disabled by deployment configuration."
UNCONFIGURED_WARNING = (
    "ML second opinion requested, but no configured pretrained/fine-tuned/feature-extractor provider "
    "is available for this exercise. Rule-based biomechanical analysis remains primary."
)
EXPERIMENTAL_SECOND_OPINION_STATUS = "optional_experimental_second_opinion"


def supported_exercise_ids() -> tuple[str, ...]:
    return registry.available_exercises()


def ml_capability_fields(
    exercise_id: str,
    *,
    model_mode: str | None = None,
    provider_status: str | None = None,
    feature_source: str | None = DEFAULT_FEATURE_SOURCE,
) -> dict[str, Any]:
    return {
        "exercise_id": exercise_id,
        "model_mode": model_mode,
        "provider_status": provider_status,
        "feature_source": feature_source,
        "supported_model_modes": list(SUPPORTED_MODEL_MODES),
        "supported_exercises": list(supported_exercise_ids()),
    }


def disabled_by_deployment_prediction(exercise_id: str) -> MLPrediction:
    return MLPrediction(
        enabled=False,
        model_version="disabled",
        warning=DISABLED_DEPLOYMENT_WARNING,
        ml_confidence_level="not_applicable",
        **ml_capability_fields(exercise_id, provider_status="disabled"),
    )


def unconfigured_prediction(exercise_id: str, reason: str | None = None) -> MLPrediction:
    warning = UNCONFIGURED_WARNING if reason is None else f"{UNCONFIGURED_WARNING} {reason}"
    return MLPrediction(
        enabled=False,
        model_version="not_configured",
        warning=warning,
        ml_confidence_level="not_applicable",
        **ml_capability_fields(exercise_id, provider_status="not_configured"),
    )


def skipped_prediction(exercise_id: str, warning: str) -> MLPrediction:
    return MLPrediction(
        enabled=False,
        model_version=MODEL_VERSION if exercise_id == "bodyweight_squat" else "skipped",
        warning=warning,
        ml_confidence_level="not_applicable",
        **ml_capability_fields(exercise_id, provider_status="skipped"),
    )


def _load_provider_catalog(path: str | None = None) -> dict[str, Any]:
    catalog_path = path or os.getenv("ML_SECOND_OPINION_CATALOG")
    if not catalog_path:
        return {}
    try:
        resolved = Path(catalog_path)
        if not resolved.exists():
            logger.warning("ML second-opinion catalog not found: %s", resolved)
            return {}
        payload = json.loads(resolved.read_text(encoding="utf-8"))
        if isinstance(payload, dict) and isinstance(payload.get("models"), dict):
            return payload["models"]
        if isinstance(payload, dict):
            return payload
    except Exception as exc:
        logger.warning("ML second-opinion catalog could not be loaded: %s", exc)
    return {}


def _call_provider(config: dict[str, Any], exercise_id: str, frames: list[dict], detected_issues: list[str]) -> MLPrediction:
    callable_path = str(config.get("callable", ""))
    module_name, separator, function_name = callable_path.partition(":")
    if not module_name or not separator or not function_name:
        return unconfigured_prediction(exercise_id, "Configured provider does not define a module:function callable.")
    try:
        module = importlib.import_module(module_name)
        provider = getattr(module, function_name)
        result = provider(
            exercise_id=exercise_id,
            frames=frames,
            detected_issues=detected_issues,
            model_config=config,
        )
        prediction = result if isinstance(result, MLPrediction) else MLPrediction(**dict(result))
        prediction.exercise_id = prediction.exercise_id or exercise_id
        prediction.supported_model_modes = prediction.supported_model_modes or list(SUPPORTED_MODEL_MODES)
        prediction.supported_exercises = prediction.supported_exercises or list(supported_exercise_ids())
        prediction.model_mode = prediction.model_mode or config.get("model_mode")
        prediction.provider_status = prediction.provider_status or ("available" if prediction.enabled else "unavailable")
        prediction.feature_source = prediction.feature_source or config.get("feature_source") or DEFAULT_FEATURE_SOURCE
        return prediction
    except Exception as exc:
        logger.warning("ML second-opinion provider failed for %s: %s", exercise_id, exc)
        return unconfigured_prediction(exercise_id, "Configured provider could not complete inference safely.")


def predict_ml_second_opinion(
    exercise_id: str,
    frames: list[dict],
    detected_issues: list[str] | None = None,
    *,
    catalog: dict[str, Any] | None = None,
) -> MLPrediction:
    detected = detected_issues or []
    if exercise_id == "bodyweight_squat":
        prediction = enrich_ml_prediction(predict_experimental_quality(frames), detected)
        prediction.model_mode = prediction.model_mode or MODEL_MODE_CLASSICAL_POSE_BASELINE
        prediction.provider_status = prediction.provider_status or ("available" if prediction.enabled else "unavailable")
        prediction.feature_source = prediction.feature_source or DEFAULT_FEATURE_SOURCE
        prediction.exercise_id = prediction.exercise_id or exercise_id
        prediction.supported_model_modes = prediction.supported_model_modes or list(SUPPORTED_MODEL_MODES)
        prediction.supported_exercises = prediction.supported_exercises or list(supported_exercise_ids())
        return prediction

    provider_catalog = catalog if catalog is not None else _load_provider_catalog()
    provider_config = provider_catalog.get(exercise_id)
    if not isinstance(provider_config, dict):
        return unconfigured_prediction(exercise_id)
    if provider_config.get("enabled") is False:
        return unconfigured_prediction(exercise_id, "Configured provider is disabled pending validation.")
    model_mode = str(provider_config.get("model_mode", "")).strip()
    if model_mode not in SUPPORTED_MODEL_MODES:
        return unconfigured_prediction(exercise_id, "Configured provider uses an unsupported model_mode.")
    prediction = _call_provider(provider_config, exercise_id, frames, detected)
    if prediction.enabled:
        prediction.warning = prediction.warning or "Experimental ML second opinion. Rule-based analysis remains primary."
    return prediction


def apply_ml_second_opinion(
    report: AnalysisResponse,
    frames: list[dict],
    include_ml: bool,
    ml_enabled: bool,
) -> AnalysisResponse:
    exercise_id = report.exercise_id or report.exercise
    if not include_ml:
        report.ml_prediction = None
        return report
    if not ml_enabled:
        report.ml_prediction = disabled_by_deployment_prediction(exercise_id)
        if DISABLED_DEPLOYMENT_WARNING not in report.validation_warnings:
            report.validation_warnings.append(DISABLED_DEPLOYMENT_WARNING)
        return report
    if report.status == "rejected":
        if exercise_id == "bodyweight_squat":
            report.ml_prediction = invalid_squat_prediction()
            report.ml_prediction.model_mode = MODEL_MODE_CLASSICAL_POSE_BASELINE
            report.ml_prediction.provider_status = "skipped"
            report.ml_prediction.feature_source = DEFAULT_FEATURE_SOURCE
            report.ml_prediction.exercise_id = exercise_id
            report.ml_prediction.supported_model_modes = list(SUPPORTED_MODEL_MODES)
            report.ml_prediction.supported_exercises = list(supported_exercise_ids())
        else:
            report.ml_prediction = skipped_prediction(
                exercise_id,
                "ML second opinion skipped because no valid movement was detected. Rule-based analysis remains primary.",
            )
        return report
    report.ml_prediction = predict_ml_second_opinion(exercise_id, frames, report.detected_issues)
    report.analysis_confidence = apply_ml_confidence_context(report.analysis_confidence, report.ml_prediction)
    return report


def experimental_ml_status_for_supported_exercise(_exercise_id: str) -> str:
    return EXPERIMENTAL_SECOND_OPINION_STATUS


__all__ = [
    "DISABLED_DEPLOYMENT_WARNING",
    "EXPERIMENTAL_SECOND_OPINION_STATUS",
    "INVALID_SQUAT_WARNING",
    "SUPPORTED_MODEL_MODES",
    "apply_ml_second_opinion",
    "experimental_ml_status_for_supported_exercise",
    "predict_ml_second_opinion",
    "supported_exercise_ids",
    "unconfigured_prediction",
]
