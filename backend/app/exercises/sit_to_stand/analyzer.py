"""End-to-end rule-based sit-to-stand landmark analyzer."""

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

from .feedback import build_sit_to_stand_feedback
from .scoring import score_sit_to_stand
from .schemas import SitToStandCountResult
from .state_machine import count_sit_to_stand_reps
from .validity import validate_sit_to_stand


def _midpoint(left: dict[str, float], right: dict[str, float]) -> dict[str, float]:
    return {key: (float(left.get(key, 0)) + float(right.get(key, 0))) / 2 for key in ("x", "y", "z", "visibility")}


def _metrics(frame: dict[str, Any]) -> tuple[float, float, float]:
    points = frame["landmarks"]
    left_knee = calculate_knee_angle(points["left_hip"], points["left_knee"], points["left_ankle"])
    right_knee = calculate_knee_angle(points["right_hip"], points["right_knee"], points["right_ankle"])
    shoulder = _midpoint(points["left_shoulder"], points["right_shoulder"])
    hip = _midpoint(points["left_hip"], points["right_hip"])
    knee = _midpoint(points["left_knee"], points["right_knee"])
    return mean([left_knee, right_knee]), calculate_hip_angle(shoulder, hip, knee), calculate_trunk_angle(shoulder, hip)


def unavailable_ml_prediction() -> MLPrediction:
    return MLPrediction(
        enabled=False, model_version="not_applicable",
        warning="ML prediction is not available for sit-to-stand yet.",
    )


class SitToStandAnalyzer(ExerciseAnalyzer):
    exercise_id = "sit_to_stand"

    def analyze(self, video_path: Path, options: dict[str, Any] | None = None) -> AnalysisResponse:
        options = options or {}
        return self.analyze_landmarks(
            extract_pose_landmarks(video_path), include_frame_data=bool(options.get("include_frame_data"))
        )

    def count_reps(self, *args: Any, **kwargs: Any) -> SitToStandCountResult:
        return count_sit_to_stand_reps(*args, **kwargs)

    def validate_input(self, *args: Any, **kwargs: Any):
        return validate_sit_to_stand(*args, **kwargs)

    def score_movement(self, *args: Any, **kwargs: Any):
        return score_sit_to_stand(*args, **kwargs)

    def generate_feedback(self, *args: Any, **kwargs: Any) -> list[str]:
        return build_sit_to_stand_feedback(*args, **kwargs)

    def analyze_landmarks(
        self, frames: list[dict[str, Any]], include_frame_data: bool = False
    ) -> AnalysisResponse:
        if not frames:
            return AnalysisResponse(
                exercise=self.exercise_id, status="rejected",
                error_code="INVALID_SIT_TO_STAND_VIDEO",
                message="No valid sit-to-stand movement was detected.", movement_score=None,
                detected_issues=["no_valid_sit_to_stand_detected"],
                feedback=build_sit_to_stand_feedback(["no_valid_sit_to_stand_detected"]),
                ml_prediction=unavailable_ml_prediction(),
                limitations=["No pose-detected frames were available."],
            )
        metrics = [_metrics(frame) for frame in frames]
        knees = [value[0] for value in metrics]
        hips = [value[1] for value in metrics]
        trunks = [value[2] for value in metrics]
        timestamps = [float(frame.get("timestamp_sec", index / 30)) for index, frame in enumerate(frames)]
        indexes = [int(frame.get("frame_index", index)) for index, frame in enumerate(frames)]
        quality = assess_pose_quality(frames)
        count = count_sit_to_stand_reps(
            knees, hips, timestamps, indexes,
            [bool(frame.get("low_confidence", False)) for frame in frames],
            quality.score, quality.pose_detection_rate,
        )
        validity = validate_sit_to_stand(knees, hips, count, quality)
        input_validity = InputValidity(
            is_valid=validity.is_valid, reason=validity.reason,
            pose_detected_frames=quality.pose_detected_frames,
            pose_detection_rate=quality.pose_detection_rate,
            overall_pose_detection_rate=quality.pose_detection_rate,
            critical_landmark_visibility=quality.critical_landmark_visibility,
            knee_angle_range=validity.knee_angle_range, hip_angle_range=validity.hip_angle_range,
            motion_variation=round((validity.knee_angle_range + validity.hip_angle_range) / 2, 2),
            valid_reps=validity.valid_reps, warnings=validity.warnings,
        )
        confidence_score = round(min(1.0, 0.55 * count.confidence + 0.45 * quality.score), 3)
        confidence = AnalysisConfidence(
            score=confidence_score if validity.is_valid else min(0.39, confidence_score),
            level="high" if validity.is_valid and confidence_score >= 0.8 else "medium" if validity.is_valid and confidence_score >= 0.6 else "low",
            reasons=[f"Rep-count confidence was {round(count.confidence * 100)}%.", f"Pose quality was {round(quality.score * 100)}%."],
            warnings=list(validity.warnings),
        )
        common = dict(
            exercise=self.exercise_id, total_reps=count.total_reps,
            average_knee_angle=round(mean(knees), 2), average_hip_angle=round(mean(hips), 2),
            average_trunk_angle=round(mean(trunks), 2),
            rep_events=[RepEvent(
                start_frame=event.start_frame, standing_frame=event.standing_frame,
                end_frame=event.end_frame, duration_sec=event.duration_sec,
                minimum_knee_angle=event.minimum_knee_angle,
                maximum_knee_angle=event.maximum_knee_angle,
            ) for event in count.rep_events],
            rep_durations=count.rep_durations, ignored_partial_reps=count.ignored_partial_reps,
            rep_count_confidence=count.confidence, pose_quality=quality,
            analysis_confidence=confidence, input_validity=input_validity,
            validation_warnings=validity.warnings, ml_prediction=unavailable_ml_prediction(),
        )
        limitations = [
            "Rule-based engineering prototype; results depend on side or oblique camera placement and joint visibility.",
            "Chair visibility is requested but is not directly detected by the current pose model.",
            "2D pose landmarks do not measure strength, balance, pain, fall risk, or clinical status.",
            "This analysis does not replace assessment by a licensed physiotherapist.",
        ]
        if not validity.is_valid:
            return AnalysisResponse(
                **common, status="rejected", error_code="INVALID_SIT_TO_STAND_VIDEO",
                message="No valid sit-to-stand movement was detected.", movement_score=None,
                detected_issues=["no_valid_sit_to_stand_detected"],
                feedback=build_sit_to_stand_feedback(["no_valid_sit_to_stand_detected"]),
                summary="The recording did not contain a complete visible sit-to-stand repetition.",
                limitations=limitations,
            )
        score = score_sit_to_stand(count, trunks, quality)
        frame_rows = [FrameAnalysis(
            frame_index=indexes[index], timestamp_sec=timestamps[index],
            knee_angle=count.smoothed_knee_angles[index], hip_angle=count.smoothed_hip_angles[index],
            trunk_angle=round(trunks[index], 2), phase=count.phases[index],
            detected_issue="excessive_trunk_lean" if trunks[index] >= 50 else None,
        ) for index in range(len(frames))]
        if include_frame_data and len(frame_rows) > 300:
            step = max(1, len(frame_rows) // 300)
            frame_rows = frame_rows[::step][:300]
        return AnalysisResponse(
            **common, status="success", movement_score=score.total,
            score_breakdown=ScoreBreakdown(
                trunk_control_score=score.trunk_control_score,
                consistency_score=score.consistency_score,
                pose_confidence_score=score.pose_confidence_score,
                completion_score=score.completion_score, control_score=score.control_score,
                symmetry_placeholder_score=score.symmetry_placeholder_score,
            ),
            detected_issues=score.issues, feedback=build_sit_to_stand_feedback(score.issues),
            summary=f"Analyzed {len(frames)} pose-detected frames and counted {count.total_reps} complete sit-to-stand repetition{'s' if count.total_reps != 1 else ''}.",
            limitations=limitations, frame_analysis=frame_rows if include_frame_data else None,
        )


sit_to_stand_analyzer = SitToStandAnalyzer()
