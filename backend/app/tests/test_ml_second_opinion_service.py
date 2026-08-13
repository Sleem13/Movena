import sys
from types import ModuleType

from app.schemas.analysis_schema import AnalysisResponse, MLPrediction
from app.services.ml_second_opinion_service import (
    SUPPORTED_MODEL_MODES,
    apply_ml_second_opinion,
    predict_ml_second_opinion,
    supported_exercise_ids,
)


def test_unconfigured_supported_exercise_reports_dl_capabilities():
    prediction = predict_ml_second_opinion("knee_extension", [{"landmarks": {}}])

    assert prediction.enabled is False
    assert prediction.provider_status == "not_configured"
    assert prediction.model_version == "not_configured"
    assert prediction.exercise_id == "knee_extension"
    assert {"pretrained_as_is", "fine_tuned", "feature_extractor"}.issubset(prediction.supported_model_modes)
    assert set(supported_exercise_ids()).issubset(set(prediction.supported_exercises))


def test_configured_fine_tuned_provider_result_is_normalized(monkeypatch):
    module = ModuleType("fake_ml_provider")

    def infer(**_kwargs):
        return {
            "enabled": True,
            "predicted_label": "controlled",
            "confidence": 0.74,
            "model_name": "test_finetuned_dl",
            "model_version": "v1",
            "warning": "Experimental provider result.",
        }

    module.infer = infer
    monkeypatch.setitem(sys.modules, "fake_ml_provider", module)

    prediction = predict_ml_second_opinion(
        "shoulder_flexion",
        [{"landmarks": {}}],
        catalog={
            "shoulder_flexion": {
                "model_mode": "fine_tuned",
                "feature_source": "video_frames",
                "callable": "fake_ml_provider:infer",
            }
        },
    )

    assert prediction.enabled is True
    assert prediction.predicted_label == "controlled"
    assert prediction.model_mode == "fine_tuned"
    assert prediction.provider_status == "available"
    assert prediction.feature_source == "video_frames"
    assert prediction.supported_model_modes == list(SUPPORTED_MODEL_MODES)


def test_apply_ml_second_opinion_skips_rejected_non_squat():
    report = AnalysisResponse(
        exercise="balance",
        exercise_id="balance",
        status="rejected",
        error_code="INVALID_BALANCE_VIDEO",
        movement_score=None,
    )

    apply_ml_second_opinion(report, [{"landmarks": {}}], include_ml=True, ml_enabled=True)

    assert report.ml_prediction is not None
    assert report.ml_prediction.enabled is False
    assert report.ml_prediction.provider_status == "skipped"
    assert "no valid movement" in report.ml_prediction.warning.lower()


def test_apply_ml_second_opinion_clears_placeholder_when_not_requested():
    report = AnalysisResponse(
        exercise="knee_extension",
        exercise_id="knee_extension",
        ml_prediction=MLPrediction(
            enabled=False,
            model_version="not_applicable",
            warning="Rule-based analyzer remains primary.",
        ),
    )

    apply_ml_second_opinion(report, [{"landmarks": {}}], include_ml=False, ml_enabled=True)

    assert report.ml_prediction is None
