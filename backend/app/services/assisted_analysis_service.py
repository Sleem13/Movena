"""Confidence-gated exercise fallback for otherwise rejected analyses."""

from __future__ import annotations

import logging
from typing import Any

from app.exercises.registry import registry
from app.ml.exercise_pose_features import extract_mediapipe_sequence_features
from app.schemas.analysis_schema import AnalysisResponse
from app.services.exercise_recognition_service import predict_exercise_from_sequence


logger = logging.getLogger(__name__)
MIN_AUTO_ROUTE_MARGIN = 0.08


def _recognition_margin(prediction: dict[str, Any]) -> float:
    ranked = list(prediction.get("top_predictions") or [])
    if len(ranked) < 2:
        return 1.0
    return float(ranked[0].get("confidence", 0.0)) - float(ranked[1].get("confidence", 0.0))


def _attach_context(
    report: AnalysisResponse,
    *,
    selected_exercise_id: str,
    recognized_exercise_id: str | None,
    confidence: float | None,
    status: str,
    message: str,
    auto_routed: bool = False,
) -> AnalysisResponse:
    report.selected_exercise_id = selected_exercise_id
    report.recognized_exercise_id = recognized_exercise_id
    report.recognition_confidence = confidence
    report.recognition_status = status
    report.recognition_message = message
    report.auto_routed = auto_routed
    return report


def apply_assisted_exercise_fallback(
    selected_exercise_id: str,
    report: AnalysisResponse,
    frames: list[dict[str, Any]],
    *,
    include_frame_data: bool = False,
) -> AnalysisResponse:
    """Try a different registered analyzer only after the selected one rejects.

    Automatic rerouting requires the temporal model's calibrated confidence
    threshold and a clear margin over its second choice.  If those safeguards
    are not met, the original result is retained for manual review.
    """

    report.selected_exercise_id = selected_exercise_id
    if report.status != "rejected" or not frames:
        return report
    try:
        sequence = extract_mediapipe_sequence_features(frames)
        if not sequence:
            return _attach_context(
                report,
                selected_exercise_id=selected_exercise_id,
                recognized_exercise_id=None,
                confidence=None,
                status="unavailable",
                message="The recording contained insufficient compatible pose data for exercise recognition.",
            )
        prediction = predict_exercise_from_sequence(sequence)
    except (ImportError, KeyError, RuntimeError, TypeError, ValueError) as exc:
        logger.warning("Assisted exercise recognition was unavailable: %s", exc)
        return report

    status = str(prediction.get("status", "not_available"))
    suggestion = prediction.get("suggested_exercise_id")
    confidence = float(prediction.get("confidence", 0.0)) if suggestion else None
    threshold = float(prediction.get("confidence_threshold") or 1.0)
    margin = _recognition_margin(prediction)
    actionable = (
        status == "success"
        and isinstance(suggestion, str)
        and suggestion in registry.available_exercises()
        and confidence is not None
        and confidence >= threshold
        and margin >= MIN_AUTO_ROUTE_MARGIN
    )
    if not suggestion:
        return _attach_context(
            report,
            selected_exercise_id=selected_exercise_id,
            recognized_exercise_id=None,
            confidence=None,
            status=status,
            message=str(prediction.get("message") or "Exercise recognition was not available."),
        )
    if suggestion == selected_exercise_id:
        return _attach_context(
            report,
            selected_exercise_id=selected_exercise_id,
            recognized_exercise_id=suggestion,
            confidence=confidence,
            status="recognized_needs_review" if actionable else "suggestion_needs_confirmation",
            message=(
                "The selected exercise was recognized, but the recording did not contain a complete scoreable repetition."
                if actionable
                else "The selected exercise may be present, but recognition confidence was not decisive enough to confirm it automatically."
            ),
        )
    if not actionable:
        return _attach_context(
            report,
            selected_exercise_id=selected_exercise_id,
            recognized_exercise_id=str(suggestion),
            confidence=confidence,
            status="suggestion_needs_confirmation",
            message="A different exercise may be present, but recognition confidence was not decisive enough to switch automatically.",
        )

    candidate = registry.get(str(suggestion)).analyze_landmarks(
        frames, include_frame_data=include_frame_data
    )
    if candidate.status != "success":
        return _attach_context(
            report,
            selected_exercise_id=selected_exercise_id,
            recognized_exercise_id=str(suggestion),
            confidence=confidence,
            status="recognized_needs_review",
            message=f"{candidate.exercise_name or suggestion} was recognized, but no complete scoreable repetition was confirmed.",
        )
    notice = (
        f"{candidate.exercise_name or suggestion} was recognized with {round(confidence * 100)}% confidence "
        "and assessed automatically."
    )
    candidate.validation_warnings.insert(0, notice)
    candidate.summary = f"{notice} {candidate.summary}".strip()
    return _attach_context(
        candidate,
        selected_exercise_id=selected_exercise_id,
        recognized_exercise_id=str(suggestion),
        confidence=confidence,
        status="auto_routed",
        message=notice,
        auto_routed=True,
    )
