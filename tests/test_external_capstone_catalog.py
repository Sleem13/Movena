import json
from pathlib import Path

from app.services.ml_second_opinion_service import predict_ml_second_opinion


CATALOG_PATH = Path("models/form_quality/external_capstone/catalog.example.json")


def test_external_capstone_candidate_is_disabled_and_identified():
    payload = json.loads(CATALOG_PATH.read_text(encoding="utf-8"))
    candidate = payload["models"]["sit_to_stand"]

    assert payload["clearance_status"] == "blocked_missing_license_and_model_provenance"
    assert candidate["enabled"] is False
    assert candidate["input_shape"] == [1, 88, 66]
    assert candidate["normalizer"] == "pelvis_width"
    assert len(candidate["sha256"]) == 64

    prediction = predict_ml_second_opinion(
        "sit_to_stand",
        [],
        catalog=payload["models"],
    )
    assert prediction.enabled is False
    assert prediction.provider_status == "not_configured"
    assert "disabled pending validation" in prediction.warning
