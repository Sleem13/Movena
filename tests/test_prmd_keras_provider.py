import hashlib

import numpy as np
import pytest

from app.ml_providers import prmd_keras_provider as provider


def _config(artifact, digest):
    return {
        "enabled": True,
        "artifact_path": artifact.name,
        "sha256": digest,
        "license_status": "approved",
        "validation_status": "approved",
        "clinician_review_status": "approved",
        "input_shape": [1, 88, 66],
        "normalizer": "pelvis_width",
        "raw_min": 0.6,
        "raw_max": 0.96,
        "model_mode": "pretrained_as_is",
    }


def test_readiness_requires_governance_approvals(tmp_path, monkeypatch):
    artifact = tmp_path / "model.keras"
    artifact.write_bytes(b"model")
    digest = hashlib.sha256(b"model").hexdigest()
    monkeypatch.setenv("PRMD_MODEL_ROOT", str(tmp_path))
    config = _config(artifact, digest)
    config["license_status"] = "blocked"

    result = provider.readiness(config)

    assert result["status"] == "blocked"
    assert "license_status" in result["reason"]


def test_readiness_verifies_artifact_hash_and_runtime(tmp_path, monkeypatch):
    artifact = tmp_path / "model.keras"
    artifact.write_bytes(b"model")
    monkeypatch.setenv("PRMD_MODEL_ROOT", str(tmp_path))
    monkeypatch.setattr(provider.importlib, "import_module", lambda _name: object())

    bad = provider.readiness(_config(artifact, "0" * 64))
    good = provider.readiness(_config(artifact, hashlib.sha256(b"model").hexdigest()))

    assert bad["status"] == "unavailable"
    assert "SHA-256" in bad["reason"]
    assert good["status"] == "ready"


def test_provider_rejects_artifact_outside_configured_root(tmp_path, monkeypatch):
    outside = tmp_path.parent / "outside.keras"
    monkeypatch.setenv("PRMD_MODEL_ROOT", str(tmp_path))

    with pytest.raises(provider.PRMDProviderError, match="inside PRMD_MODEL_ROOT"):
        provider._artifact_path({"artifact_path": str(outside)})


def test_infer_returns_verified_experimental_quality(monkeypatch, tmp_path):
    artifact = tmp_path / "model.keras"
    artifact.write_bytes(b"model")
    digest = hashlib.sha256(b"model").hexdigest()
    config = _config(artifact, digest)
    monkeypatch.setenv("PRMD_MODEL_ROOT", str(tmp_path))
    monkeypatch.setattr(provider, "readiness", lambda _config: {"status": "ready", "reason": "ok"})
    monkeypatch.setattr(
        provider,
        "prepare_prmd_model_input",
        lambda *_args, **_kwargs: np.zeros((1, 88, 66), dtype=np.float32),
    )

    class Model:
        input_shape = (None, 88, 66)

        @staticmethod
        def predict(model_input, verbose=0):
            assert model_input.shape == (1, 88, 66)
            assert verbose == 0
            return np.asarray([[0.888]], dtype=np.float32)

    monkeypatch.setattr(provider, "_load_model", lambda *_args: Model())

    prediction = provider.infer(
        exercise_id="sit_to_stand",
        frames=[{"landmarks": {}}],
        detected_issues=[],
        model_config=config,
    )

    assert prediction.enabled is True
    assert prediction.experimental_quality_score == 80
    assert prediction.predicted_label == "movement_pattern_consistent"
    assert prediction.confidence is None
    assert prediction.artifact_verified is True
    assert prediction.validation_status == "approved"
