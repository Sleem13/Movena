"""Confidence aggregation and safe experimental-ML disagreement wording."""

from __future__ import annotations

from statistics import mean

from app.core.exercise_thresholds import ML_LOW_CONFIDENCE_THRESHOLD
from app.schemas.analysis_schema import AnalysisConfidence, MLPrediction, PoseQuality


DISAGREEMENT_NOTE = (
    "The experimental ML prediction disagrees with rule-based analysis. "
    "Rule-based biomechanical feedback remains primary."
)

LABEL_TO_ISSUES = {
    "squat_correct": set(),
    "squat_shallow_depth": {"poor_depth", "possible_poor_depth"},
    "squat_knee_valgus": {"possible_knee_valgus"},
    "squat_trunk_lean": {"excessive_trunk_lean", "possible_excessive_trunk_lean"},
    "squat_fast_uncontrolled": {"inconsistent_movement"},
}


def enrich_ml_prediction(prediction: MLPrediction, detected_issues: list[str]) -> MLPrediction:
    if not prediction.enabled:
        return prediction
    confidence = prediction.confidence
    prediction.ml_confidence_level = (
        "unknown" if confidence is None else "low" if confidence < ML_LOW_CONFIDENCE_THRESHOLD else "medium" if confidence < 0.80 else "high"
    )
    expected = LABEL_TO_ISSUES.get(prediction.predicted_label or "")
    rule_issues = set(detected_issues) - {"low_landmark_confidence"}
    if expected is None:
        prediction.agrees_with_rule_based = None
    elif not expected:
        prediction.agrees_with_rule_based = not rule_issues
    else:
        prediction.agrees_with_rule_based = bool(expected & rule_issues)
    if prediction.agrees_with_rule_based is False:
        prediction.disagreement_note = DISAGREEMENT_NOTE
    return prediction


def calculate_analysis_confidence(
    pose_quality: PoseQuality,
    rep_count_confidence: float,
    smoothed_angles: list[float],
    ml_prediction: MLPrediction | None = None,
) -> AnalysisConfidence:
    changes = [abs(right - left) for left, right in zip(smoothed_angles, smoothed_angles[1:])]
    average_change = mean(changes) if changes else 0.0
    angle_stability = max(0.0, min(1.0, 1 - (average_change / 20)))
    camera_suitability = 1.0 if pose_quality.camera_view == "front_or_oblique" else 0.75
    factors = [pose_quality.score, rep_count_confidence, angle_stability, camera_suitability]
    weights = [0.45, 0.25, 0.20, 0.10]
    score = sum(value * weight for value, weight in zip(factors, weights))
    reasons = [
        f"Pose quality was {pose_quality.level}.",
        f"Rep-count confidence was {round(rep_count_confidence * 100)}%.",
        f"Angle-signal stability was {round(angle_stability * 100)}%.",
    ]
    warnings = list(pose_quality.warnings)
    if ml_prediction and ml_prediction.enabled and ml_prediction.agrees_with_rule_based is False:
        warnings.append(DISAGREEMENT_NOTE)
        if (ml_prediction.confidence or 0) >= ML_LOW_CONFIDENCE_THRESHOLD:
            score *= 0.95
    score = round(max(0.0, min(1.0, score)), 3)
    level = "high" if score >= 0.80 else "medium" if score >= 0.60 else "low"
    if level == "low":
        warnings.append("Review recording quality before relying on detailed movement observations.")
    return AnalysisConfidence(score=score, level=level, reasons=reasons, warnings=warnings)


def apply_ml_confidence_context(
    confidence: AnalysisConfidence | None, prediction: MLPrediction
) -> AnalysisConfidence | None:
    """Add ML agreement context without changing rule-based movement output."""
    if confidence is None or not prediction.enabled:
        return confidence
    if prediction.agrees_with_rule_based is True:
        confidence.reasons.append("The optional experimental ML output agreed with the rule-based category.")
    elif prediction.agrees_with_rule_based is False:
        if DISAGREEMENT_NOTE not in confidence.warnings:
            confidence.warnings.append(DISAGREEMENT_NOTE)
        if (prediction.confidence or 0) >= ML_LOW_CONFIDENCE_THRESHOLD:
            confidence.score = round(confidence.score * 0.95, 3)
            confidence.level = "high" if confidence.score >= 0.80 else "medium" if confidence.score >= 0.60 else "low"
    return confidence
