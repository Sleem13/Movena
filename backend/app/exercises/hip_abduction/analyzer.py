"""End-to-end rule-based standing hip-abduction landmark analyzer."""

from __future__ import annotations

from pathlib import Path
from statistics import mean
from typing import Any

from app.exercises.base import ExerciseAnalyzer
from app.schemas.analysis_schema import AnalysisConfidence, AnalysisResponse, FrameAnalysis, InputValidity, MLPrediction, RepEvent, ScoreBreakdown
from app.services.angle_calculation_service import calculate_angle, calculate_trunk_angle
from app.services.pose_estimation_service import extract_pose_landmarks
from app.services.pose_quality_service import assess_pose_quality

from .feedback import build_hip_abduction_feedback
from .scoring import score_hip_abduction
from .schemas import HipAbductionCountResult
from .state_machine import count_hip_abduction_reps
from .thresholds import ABDUCTED_ANGLE_MIN, PELVIC_HIKE_Y_DIFFERENCE, TRUNK_COMPENSATION_ANGLE
from .validity import validate_hip_abduction


def unavailable_ml_prediction() -> MLPrediction:
    return MLPrediction(enabled=False, model_version="not_applicable", warning="ML prediction is not applicable for hip abduction; rule-based analysis remains primary.")


def _visibility(frame: dict[str, Any], side: str) -> float:
    points = frame.get("landmarks", {})
    values = [float(points.get(f"{side}_{joint}", {}).get("visibility", 0)) for joint in ("shoulder", "hip", "knee", "ankle")]
    other_hip = float(points.get(f"{'right' if side == 'left' else 'left'}_hip", {}).get("visibility", 0))
    return min(values + [other_hip]) if values else 0.0


def _metrics(frame: dict[str, Any], side: str) -> tuple[float, float, float, bool] | None:
    points = frame.get("landmarks", {})
    shoulder, hip, knee, ankle = (points.get(f"{side}_{joint}") for joint in ("shoulder", "hip", "knee", "ankle"))
    other_hip = points.get(f"{'right' if side == 'left' else 'left'}_hip")
    if not all((shoulder, hip, knee, ankle, other_hip)):
        return None
    trunk_leg_angle = calculate_angle(shoulder, hip, ankle)
    abduction_angle = max(0.0, min(90.0, abs(180.0 - trunk_leg_angle)))
    trunk_angle = calculate_trunk_angle(shoulder, hip)
    pelvic_hike = float(other_hip["y"]) - float(hip["y"]) > PELVIC_HIKE_Y_DIFFERENCE
    return round(abduction_angle, 2), trunk_angle, _visibility(frame, side), pelvic_hike


def _select_side(frames: list[dict[str, Any]]) -> str:
    scores = {}
    for side in ("left", "right"):
        metrics = [value for frame in frames if (value := _metrics(frame, side)) is not None]
        if not metrics:
            scores[side] = 0.0
            continue
        angles = [value[0] for value in metrics]
        visibility = mean(value[2] for value in metrics)
        motion = min(1.0, (max(angles) - min(angles)) / 35.0)
        scores[side] = .60 * visibility + .40 * motion
    return max(scores, key=scores.get)


class HipAbductionAnalyzer(ExerciseAnalyzer):
    exercise_id = "hip_abduction"

    def analyze(self, video_path: Path, options: dict[str, Any] | None = None) -> AnalysisResponse:
        options = options or {}
        return self.analyze_landmarks(extract_pose_landmarks(video_path), include_frame_data=bool(options.get("include_frame_data")))

    def count_reps(self, *args: Any, **kwargs: Any) -> HipAbductionCountResult:
        return count_hip_abduction_reps(*args, **kwargs)

    def validate_input(self, *args: Any, **kwargs: Any):
        return validate_hip_abduction(*args, **kwargs)

    def score_movement(self, *args: Any, **kwargs: Any):
        return score_hip_abduction(*args, **kwargs)

    def generate_feedback(self, *args: Any, **kwargs: Any) -> list[str]:
        return build_hip_abduction_feedback(*args, **kwargs)

    def _empty_rejection(self) -> AnalysisResponse:
        return AnalysisResponse(exercise=self.exercise_id, exercise_id=self.exercise_id, exercise_name="Hip Abduction", status="rejected", error_code="INVALID_HIP_ABDUCTION_VIDEO", message="No valid hip abduction movement was detected.", movement_score=None, valid_reps=0, detected_issues=["no_valid_hip_abduction_detected"], feedback=build_hip_abduction_feedback(["no_valid_hip_abduction_detected"]), ml_prediction=unavailable_ml_prediction(), limitations=["No usable pose-detected frames were available."])

    def analyze_landmarks(self, frames: list[dict[str, Any]], include_frame_data: bool = False) -> AnalysisResponse:
        if not frames:
            return self._empty_rejection()
        side = _select_side(frames)
        usable = [(frame, metrics) for frame in frames if (metrics := _metrics(frame, side)) is not None]
        if not usable:
            return self._empty_rejection()
        usable_frames = [item[0] for item in usable]
        angles = [item[1][0] for item in usable]
        trunks = [item[1][1] for item in usable]
        visibilities = [item[1][2] for item in usable]
        hikes = [item[1][3] for item in usable]
        timestamps = [float(frame.get("timestamp_sec", index / 30)) for index, frame in enumerate(usable_frames)]
        indexes = [int(frame.get("frame_index", index)) for index, frame in enumerate(usable_frames)]
        quality = assess_pose_quality(frames)
        if quality.camera_view == "side_or_oblique":
            old_warning = quality.camera_view_warning
            quality.camera_view_warning = "A stable front view is preferred for standing hip-abduction review."
            quality.warnings = [warning for warning in quality.warnings if warning != old_warning]
            quality.warnings.insert(0, quality.camera_view_warning)
        selected_visibility = round(mean(visibilities), 3)
        count = count_hip_abduction_reps(angles, timestamps, indexes, [bool(frame.get("low_confidence", False)) or visibility < .5 for frame, visibility in zip(usable_frames, visibilities)], quality.score, quality.pose_detection_rate)
        validity = validate_hip_abduction(angles, count, quality, selected_visibility)
        input_validity = InputValidity(is_valid=validity.is_valid, reason=validity.reason, pose_detected_frames=quality.pose_detected_frames, pose_detection_rate=quality.pose_detection_rate, overall_pose_detection_rate=quality.pose_detection_rate, critical_landmark_visibility=selected_visibility, knee_angle_range=0, hip_angle_range=validity.angle_range, motion_variation=validity.angle_range, valid_reps=validity.valid_reps, warnings=validity.warnings, hip_abduction_angle_range=validity.angle_range)
        confidence_score = round(min(1.0, .55 * count.confidence + .25 * quality.score + .20 * selected_visibility), 3)
        confidence = AnalysisConfidence(score=confidence_score if validity.is_valid else min(.39, confidence_score), level="high" if validity.is_valid and confidence_score >= .8 else "medium" if validity.is_valid and confidence_score >= .6 else "low", reasons=[f"Rep-count confidence was {round(count.confidence * 100)}%.", f"Selected {side}-side landmark visibility was {round(selected_visibility * 100)}%."], warnings=list(validity.warnings))
        common = dict(exercise=self.exercise_id, exercise_id=self.exercise_id, exercise_name="Hip Abduction", total_reps=count.total_reps, valid_reps=count.valid_reps, average_hip_abduction_angle=round(mean(angles), 2), average_hip_angle=round(mean(angles), 2), average_trunk_angle=round(mean(trunks), 2), rep_events=[RepEvent(start_frame=event.start_frame, standing_frame=event.abducted_frame, end_frame=event.end_frame, duration_sec=event.duration_sec, minimum_knee_angle=event.minimum_angle, maximum_knee_angle=event.maximum_angle) for event in count.rep_events], rep_durations=count.rep_durations, ignored_partial_reps=count.ignored_partial_reps, rep_count_confidence=count.confidence, phase_transitions=count.phase_transitions, pose_quality=quality, analysis_confidence=confidence, input_validity=input_validity, validation_warnings=validity.warnings, ml_prediction=unavailable_ml_prediction())
        limitations = ["Rule-based MVP thresholds are adjustable engineering defaults and are not clinically validated.", "A stable front view with the pelvis, hip, knee, ankle, and trunk visible is preferred.", "2D pose does not measure strength, balance capacity, pain, tissue status, joint loading, or treatment suitability.", "AI feedback supports exercise monitoring and does not replace physiotherapist assessment."]
        if not validity.is_valid:
            return AnalysisResponse(**common, status="rejected", error_code="INVALID_HIP_ABDUCTION_VIDEO", message="No valid hip abduction movement was detected.", movement_score=None, score_breakdown=None, detected_issues=["no_valid_hip_abduction_detected"], feedback=build_hip_abduction_feedback(["no_valid_hip_abduction_detected"]), summary="The recording did not contain a complete visible neutral-abducted-neutral repetition.", limitations=limitations)
        score = score_hip_abduction(count, quality, selected_visibility, trunks, sum(hikes) / len(hikes))
        frame_rows = [FrameAnalysis(frame_index=indexes[index], timestamp_sec=timestamps[index], knee_angle=0, hip_angle=count.smoothed_angles[index], trunk_angle=round(trunks[index], 2), hip_abduction_angle=count.smoothed_angles[index], phase=count.phases[index], detected_issue=("limited_observed_hip_abduction_range" if count.phases[index] == "abducted" and count.smoothed_angles[index] < ABDUCTED_ANGLE_MIN else "possible_trunk_lean_compensation" if trunks[index] >= TRUNK_COMPENSATION_ANGLE else "possible_pelvic_hiking_pattern" if hikes[index] else None)) for index in range(len(usable_frames))]
        if include_frame_data and len(frame_rows) > 300:
            step = max(1, len(frame_rows) // 300)
            frame_rows = frame_rows[::step][:300]
        return AnalysisResponse(**common, status="success", movement_score=score.total, score_breakdown=ScoreBreakdown(abduction_range_score=score.abduction_range_score, control_score=score.control_score, consistency_score=score.consistency_score, posture_visibility_score=score.posture_visibility_score, rep_completion_score=score.rep_completion_score, pelvis_trunk_stability_score=score.pelvis_trunk_stability_score, pose_confidence_score=score.posture_visibility_score), detected_issues=score.issues, feedback=build_hip_abduction_feedback(score.issues), summary=f"Analyzed {len(usable_frames)} pose-detected frames using the {side} leg and counted {count.total_reps} complete hip abduction repetition{'s' if count.total_reps != 1 else ''}.", limitations=limitations, frame_analysis=frame_rows if include_frame_data else None)


hip_abduction_analyzer = HipAbductionAnalyzer()
