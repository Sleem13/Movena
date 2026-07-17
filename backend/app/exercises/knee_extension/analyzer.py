"""End-to-end rule-based knee-extension landmark analyzer."""

from __future__ import annotations

from pathlib import Path
from statistics import mean
from typing import Any

from app.exercises.base import ExerciseAnalyzer
from app.schemas.analysis_schema import (
    AnalysisConfidence, AnalysisResponse, FrameAnalysis, InputValidity, MLPrediction,
    RepEvent, ScoreBreakdown,
)
from app.services.angle_calculation_service import calculate_hip_angle, calculate_knee_angle, calculate_trunk_angle
from app.services.pose_estimation_service import extract_pose_landmarks
from app.services.pose_quality_service import assess_pose_quality

from .feedback import build_knee_extension_feedback
from .scoring import score_knee_extension
from .schemas import KneeExtensionCountResult
from .state_machine import count_knee_extension_reps
from .thresholds import EXTENDED_KNEE_ANGLE_MIN, TRUNK_COMPENSATION_ANGLE
from .validity import validate_knee_extension


def unavailable_ml_prediction() -> MLPrediction:
    return MLPrediction(
        enabled=False, model_version="not_applicable",
        warning="ML prediction is not applicable for knee extension; rule-based analysis remains primary.",
    )


def _point_visibility(frame: dict[str, Any], side: str) -> float:
    points = frame.get("landmarks", {})
    values = [float(points.get(f"{side}_{joint}", {}).get("visibility", 0)) for joint in ("hip", "knee", "ankle")]
    return min(values) if values else 0.0


def _select_side(frames: list[dict[str, Any]]) -> str:
    scores = {
        side: mean(_point_visibility(frame, side) for frame in frames)
        for side in ("left", "right")
    }
    return max(scores, key=scores.get)


def _metrics(frame: dict[str, Any], side: str) -> tuple[float, float, float, float] | None:
    points = frame.get("landmarks", {})
    hip, knee, ankle = (points.get(f"{side}_{joint}") for joint in ("hip", "knee", "ankle"))
    if not hip or not knee or not ankle:
        return None
    shoulder = points.get(f"{side}_shoulder") or points.get(f"{'right' if side == 'left' else 'left'}_shoulder")
    knee_angle = calculate_knee_angle(hip, knee, ankle)
    hip_angle = calculate_hip_angle(shoulder, hip, knee) if shoulder else 0.0
    trunk_angle = calculate_trunk_angle(shoulder, hip) if shoulder else 0.0
    return knee_angle, hip_angle, trunk_angle, _point_visibility(frame, side)


class KneeExtensionAnalyzer(ExerciseAnalyzer):
    exercise_id = "knee_extension"

    def analyze(self, video_path: Path, options: dict[str, Any] | None = None) -> AnalysisResponse:
        options = options or {}
        return self.analyze_landmarks(
            extract_pose_landmarks(video_path), include_frame_data=bool(options.get("include_frame_data"))
        )

    def count_reps(self, *args: Any, **kwargs: Any) -> KneeExtensionCountResult:
        return count_knee_extension_reps(*args, **kwargs)

    def validate_input(self, *args: Any, **kwargs: Any):
        return validate_knee_extension(*args, **kwargs)

    def score_movement(self, *args: Any, **kwargs: Any):
        return score_knee_extension(*args, **kwargs)

    def generate_feedback(self, *args: Any, **kwargs: Any) -> list[str]:
        return build_knee_extension_feedback(*args, **kwargs)

    def _empty_rejection(self) -> AnalysisResponse:
        return AnalysisResponse(
            exercise=self.exercise_id, exercise_id=self.exercise_id, exercise_name="Knee Extension",
            status="rejected", error_code="INVALID_KNEE_EXTENSION_VIDEO",
            message="No valid knee extension movement was detected.", movement_score=None,
            valid_reps=0, detected_issues=["no_valid_knee_extension_detected"],
            feedback=build_knee_extension_feedback(["no_valid_knee_extension_detected"]),
            ml_prediction=unavailable_ml_prediction(),
            limitations=["No usable pose-detected frames were available."],
        )

    def analyze_landmarks(self, frames: list[dict[str, Any]], include_frame_data: bool = False) -> AnalysisResponse:
        if not frames:
            return self._empty_rejection()
        side = _select_side(frames)
        usable: list[tuple[dict[str, Any], tuple[float, float, float, float]]] = []
        for frame in frames:
            metrics = _metrics(frame, side)
            if metrics is not None:
                usable.append((frame, metrics))
        if not usable:
            return self._empty_rejection()

        usable_frames = [item[0] for item in usable]
        knees = [item[1][0] for item in usable]
        hips = [item[1][1] for item in usable]
        trunks = [item[1][2] for item in usable]
        visibilities = [item[1][3] for item in usable]
        timestamps = [float(frame.get("timestamp_sec", index / 30)) for index, frame in enumerate(usable_frames)]
        indexes = [int(frame.get("frame_index", index)) for index, frame in enumerate(usable_frames)]
        quality = assess_pose_quality(frames)
        selected_visibility = round(mean(visibilities), 3)
        count = count_knee_extension_reps(
            knees, timestamps, indexes,
            [bool(frame.get("low_confidence", False)) or visibility < 0.5 for frame, visibility in zip(usable_frames, visibilities)],
            quality.score, quality.pose_detection_rate,
        )
        validity = validate_knee_extension(knees, count, quality, selected_visibility)
        input_validity = InputValidity(
            is_valid=validity.is_valid, reason=validity.reason,
            pose_detected_frames=quality.pose_detected_frames,
            pose_detection_rate=quality.pose_detection_rate,
            overall_pose_detection_rate=quality.pose_detection_rate,
            critical_landmark_visibility=selected_visibility,
            knee_angle_range=validity.knee_angle_range,
            hip_angle_range=round(max(hips) - min(hips), 2) if hips else 0,
            motion_variation=validity.knee_angle_range,
            valid_reps=validity.valid_reps, warnings=validity.warnings,
        )
        confidence_score = round(min(1.0, 0.55 * count.confidence + 0.25 * quality.score + 0.20 * selected_visibility), 3)
        confidence = AnalysisConfidence(
            score=confidence_score if validity.is_valid else min(0.39, confidence_score),
            level="high" if validity.is_valid and confidence_score >= 0.8 else "medium" if validity.is_valid and confidence_score >= 0.6 else "low",
            reasons=[
                f"Rep-count confidence was {round(count.confidence * 100)}%.",
                f"Selected {side}-side landmark visibility was {round(selected_visibility * 100)}%.",
            ], warnings=list(validity.warnings),
        )
        common = dict(
            exercise=self.exercise_id, exercise_id=self.exercise_id, exercise_name="Knee Extension",
            total_reps=count.total_reps, valid_reps=count.valid_reps,
            average_knee_angle=round(mean(knees), 2), average_hip_angle=round(mean(hips), 2),
            average_trunk_angle=round(mean(trunks), 2),
            rep_events=[RepEvent(
                start_frame=event.start_frame, standing_frame=event.extended_frame,
                end_frame=event.end_frame, duration_sec=event.duration_sec,
                minimum_knee_angle=event.minimum_knee_angle, maximum_knee_angle=event.maximum_knee_angle,
            ) for event in count.rep_events],
            rep_durations=count.rep_durations, ignored_partial_reps=count.ignored_partial_reps,
            rep_count_confidence=count.confidence, phase_transitions=count.phase_transitions,
            pose_quality=quality, analysis_confidence=confidence, input_validity=input_validity,
            validation_warnings=validity.warnings, ml_prediction=unavailable_ml_prediction(),
        )
        limitations = [
            "Rule-based MVP thresholds are adjustable engineering defaults and are not clinically validated.",
            "A side view with the seated hip, knee, and ankle visible is preferred.",
            "2D pose does not measure joint torque, muscle strength, pain, tissue status, or treatment suitability.",
            "AI feedback supports exercise monitoring and does not replace physiotherapist assessment.",
        ]
        if not validity.is_valid:
            return AnalysisResponse(
                **common, status="rejected", error_code="INVALID_KNEE_EXTENSION_VIDEO",
                message="No valid knee extension movement was detected.", movement_score=None,
                score_breakdown=None, detected_issues=["no_valid_knee_extension_detected"],
                feedback=build_knee_extension_feedback(["no_valid_knee_extension_detected"]),
                summary="The recording did not contain a complete visible flexion-extension-flexion repetition.",
                limitations=limitations,
            )

        score = score_knee_extension(count, quality, selected_visibility, trunks)
        frame_rows = [FrameAnalysis(
            frame_index=indexes[index], timestamp_sec=timestamps[index],
            knee_angle=count.smoothed_knee_angles[index], hip_angle=round(hips[index], 2),
            trunk_angle=round(trunks[index], 2), phase=count.phases[index],
            detected_issue=(
                "limited_knee_extension" if count.phases[index] == "extended" and count.smoothed_knee_angles[index] < EXTENDED_KNEE_ANGLE_MIN
                else "possible_compensation" if trunks[index] >= TRUNK_COMPENSATION_ANGLE else None
            ),
        ) for index in range(len(usable_frames))]
        if include_frame_data and len(frame_rows) > 300:
            step = max(1, len(frame_rows) // 300)
            frame_rows = frame_rows[::step][:300]
        return AnalysisResponse(
            **common, status="success", movement_score=score.total,
            score_breakdown=ScoreBreakdown(
                extension_range_score=score.extension_range_score,
                control_score=score.control_score, consistency_score=score.consistency_score,
                posture_visibility_score=score.posture_visibility_score,
                rep_completion_score=score.rep_completion_score,
                pose_confidence_score=score.posture_visibility_score,
            ),
            detected_issues=score.issues, feedback=build_knee_extension_feedback(score.issues),
            summary=f"Analyzed {len(usable_frames)} pose-detected frames using the {side} side and counted {count.total_reps} complete knee extension repetition{'s' if count.total_reps != 1 else ''}.",
            limitations=limitations, frame_analysis=frame_rows if include_frame_data else None,
        )


knee_extension_analyzer = KneeExtensionAnalyzer()

