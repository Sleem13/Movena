"""Governed Keras provider for external UI-PRMD form-quality models."""

from __future__ import annotations

import hashlib
import importlib
import os
from functools import lru_cache
from pathlib import Path
from typing import Any

import numpy as np

from app.schemas.analysis_schema import MLPrediction
from app.services.prmd_feature_adapter_service import prepare_prmd_model_input


REPO_ROOT = Path(__file__).resolve().parents[3]
DEFAULT_MODEL_ROOT = REPO_ROOT / "models" / "form_quality" / "external_capstone" / "artifacts"
REQUIRED_APPROVALS = ("license_status", "validation_status", "clinician_review_status")


class PRMDProviderError(RuntimeError):
    pass


def _model_root() -> Path:
    configured = os.getenv("PRMD_MODEL_ROOT", "").strip()
    return Path(configured or DEFAULT_MODEL_ROOT).expanduser().resolve()


def _artifact_path(model_config: dict[str, Any]) -> Path:
    configured = str(model_config.get("artifact_path", "")).strip()
    if not configured:
        raise PRMDProviderError("PRMD provider artifact_path is not configured.")
    root = _model_root()
    candidate = Path(configured)
    resolved = (candidate if candidate.is_absolute() else root / candidate).resolve()
    try:
        resolved.relative_to(root)
    except ValueError as exc:
        raise PRMDProviderError("PRMD model artifact must remain inside PRMD_MODEL_ROOT.") from exc
    return resolved


def _approval_blockers(model_config: dict[str, Any]) -> list[str]:
    return [field for field in REQUIRED_APPROVALS if model_config.get(field) != "approved"]


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def readiness(model_config: dict[str, Any]) -> dict[str, Any]:
    if model_config.get("enabled") is False:
        return {"status": "disabled", "reason": "Provider is disabled by catalog configuration."}
    blockers = _approval_blockers(model_config)
    if blockers:
        return {
            "status": "blocked",
            "reason": "Required approvals are incomplete: " + ", ".join(blockers) + ".",
        }
    try:
        artifact = _artifact_path(model_config)
    except PRMDProviderError as exc:
        return {"status": "misconfigured", "reason": str(exc)}
    if not artifact.is_file():
        return {"status": "unavailable", "reason": "Configured model artifact is missing."}
    expected_hash = str(model_config.get("sha256", "")).lower()
    if len(expected_hash) != 64 or _sha256(artifact) != expected_hash:
        return {"status": "unavailable", "reason": "Model artifact SHA-256 verification failed."}
    try:
        importlib.import_module("tensorflow")
    except (ImportError, OSError):
        return {
            "status": "unavailable",
            "reason": "Optional TensorFlow runtime is missing or cannot load its native dependencies.",
        }
    return {"status": "ready", "reason": "Artifact, approvals, and runtime checks passed."}


@lru_cache(maxsize=4)
def _load_model(path: str, expected_hash: str):
    from tensorflow.keras.models import load_model

    artifact = Path(path)
    if _sha256(artifact) != expected_hash:
        raise PRMDProviderError("Model artifact changed after readiness verification.")
    return load_model(artifact, compile=False)


def _quality_label(score: int) -> str:
    if score >= 80:
        return "movement_pattern_consistent"
    if score >= 60:
        return "review_recommended"
    return "movement_pattern_differs"


def infer(
    *,
    exercise_id: str,
    frames: list[dict],
    detected_issues: list[str],
    model_config: dict[str, Any],
) -> MLPrediction:
    provider_readiness = readiness(model_config)
    if provider_readiness["status"] != "ready":
        raise PRMDProviderError(str(provider_readiness["reason"]))

    target_frames = int(model_config["input_shape"][1])
    feature_count = int(model_config["input_shape"][2])
    if feature_count != 66:
        raise PRMDProviderError("PRMD provider requires a 66-feature input contract.")
    model_input = prepare_prmd_model_input(
        frames,
        target_frames=target_frames,
        normalizer=str(model_config["normalizer"]),
        min_visibility=float(model_config.get("min_visibility", 0.45)),
    )

    artifact = _artifact_path(model_config)
    expected_hash = str(model_config["sha256"]).lower()
    model = _load_model(str(artifact), expected_hash)
    configured_shape = tuple(model_config["input_shape"])
    model_shape = tuple(getattr(model, "input_shape", configured_shape))
    if model_shape[-2:] != configured_shape[-2:]:
        raise PRMDProviderError("Loaded model input shape does not match the catalog contract.")

    output = np.asarray(model.predict(model_input, verbose=0), dtype=np.float64).reshape(-1)
    if output.size != 1 or not np.isfinite(output[0]):
        raise PRMDProviderError("Loaded model returned an invalid scalar output.")
    raw_value = float(output[0])
    raw_min = float(model_config["raw_min"])
    raw_max = float(model_config["raw_max"])
    if raw_max <= raw_min:
        raise PRMDProviderError("Model calibration bounds are invalid.")
    quality_score = int(round(np.clip((raw_value - raw_min) / (raw_max - raw_min), 0.0, 1.0) * 100))

    return MLPrediction(
        enabled=True,
        predicted_label=_quality_label(quality_score),
        confidence=None,
        experimental_quality_score=quality_score,
        model_name=str(model_config.get("model_name", "UI-PRMD form-quality BiLSTM")),
        model_version=f"sha256:{expected_hash[:12]}",
        model_mode=str(model_config["model_mode"]),
        provider_status="available",
        feature_source="prmd_22_joint_sequence",
        exercise_id=exercise_id,
        artifact_verified=True,
        validation_status=str(model_config["validation_status"]),
        warning=(
            "Experimental movement-intelligence comparison for therapist review. "
            "Rule-based analysis remains primary and this output must not guide diagnosis or treatment."
        ),
    )


__all__ = ["PRMDProviderError", "infer", "readiness"]
