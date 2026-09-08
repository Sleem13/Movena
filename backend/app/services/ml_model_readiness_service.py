"""Read-only deployment readiness for optional ML providers."""

from __future__ import annotations

import importlib
from typing import Any

from app.services.ml_second_opinion_service import _load_provider_catalog, supported_exercise_ids


def _provider_readiness(config: dict[str, Any]) -> dict[str, Any]:
    callable_path = str(config.get("callable", ""))
    module_name, separator, _function_name = callable_path.partition(":")
    if not module_name or not separator:
        return {"status": "misconfigured", "reason": "Provider callable is missing."}
    try:
        module = importlib.import_module(module_name)
        check = getattr(module, "readiness", None)
        if not callable(check):
            return {"status": "unknown", "reason": "Provider does not expose a readiness check."}
        result = check(config)
        return {"status": str(result["status"]), "reason": str(result["reason"])}
    except Exception:
        return {"status": "unavailable", "reason": "Provider readiness check could not complete safely."}


def ml_model_readiness() -> dict[str, Any]:
    catalog = _load_provider_catalog()
    models = []
    for exercise_id in supported_exercise_ids():
        if exercise_id == "bodyweight_squat":
            models.append({
                "exercise_id": exercise_id,
                "status": "available",
                "provider": "trusted_sprint_5_baseline",
                "reason": "Built-in experimental baseline is loaded on demand.",
            })
            continue
        config = catalog.get(exercise_id)
        if not isinstance(config, dict):
            models.append({
                "exercise_id": exercise_id,
                "status": "not_configured",
                "provider": None,
                "reason": "No optional model provider is configured.",
            })
            continue
        models.append({
            "exercise_id": exercise_id,
            "provider": str(config.get("callable", "")).partition(":")[0] or None,
            **_provider_readiness(config),
        })
    return {"models": models}


def validate_required_ml_models(required_exercises: list[str]) -> None:
    if not required_exercises:
        return
    status_by_exercise = {
        item["exercise_id"]: item
        for item in ml_model_readiness()["models"]
    }
    failures = [
        f"{exercise_id}: {status_by_exercise.get(exercise_id, {}).get('reason', 'not found')}"
        for exercise_id in required_exercises
        if status_by_exercise.get(exercise_id, {}).get("status") not in {"ready", "available"}
    ]
    if failures:
        raise RuntimeError("Required ML providers are not ready: " + "; ".join(failures))


__all__ = ["ml_model_readiness", "validate_required_ml_models"]
