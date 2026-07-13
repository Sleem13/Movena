from app.schemas.analysis_schema import MLPrediction
from app.services.analysis_confidence_service import DISAGREEMENT_NOTE, enrich_ml_prediction


def prediction(label, confidence):
    return MLPrediction(
        enabled=True, predicted_label=label, confidence=confidence,
        model_name="svc_rbf", warning="Experimental baseline model. Not clinically validated.",
    )


def test_ml_low_confidence_is_marked():
    result = enrich_ml_prediction(prediction("squat_correct", 0.61), [])
    assert result.ml_confidence_level == "low"
    assert result.agrees_with_rule_based is True


def test_ml_disagreement_does_not_override_rule_based_output():
    issues = ["poor_depth"]
    result = enrich_ml_prediction(prediction("squat_correct", 0.9), issues)
    assert issues == ["poor_depth"]
    assert result.agrees_with_rule_based is False
    assert result.disagreement_note == DISAGREEMENT_NOTE
