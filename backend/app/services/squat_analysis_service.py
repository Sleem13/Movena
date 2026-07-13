from statistics import mean, pstdev
from typing import Any

from app.schemas.analysis_schema import AnalysisResponse, FrameAnalysis
from app.core.exercise_thresholds import (
    INCONSISTENT_DEPTH_STD_DEG,
    KNEE_VALGUS_FRAME_RATIO,
    KNEE_VALGUS_MARGIN_NORMALIZED,
    LOW_CONFIDENCE_FRAME_RATIO,
    SQUAT_DEPTH_KNEE_ANGLE_DEG,
    STANDING_KNEE_ANGLE_DEG,
    TRUNK_LEAN_THRESHOLD_DEG,
)
from app.services.angle_calculation_service import (
    calculate_hip_angle,
    calculate_knee_angle,
    calculate_trunk_angle,
)
from app.services.feedback_service import DISCLAIMER, build_feedback
from app.services.analysis_confidence_service import calculate_analysis_confidence
from app.services.pose_quality_service import assess_pose_quality
from app.services.rep_counting_service import count_squat_reps
from app.services.squat_scoring_service import score_squat
from app.services.squat_validity_service import validate_squat_attempt

def _avg_point(left: dict[str, float], right: dict[str, float]) -> dict[str, float]:
    return {
        "x": (left["x"] + right["x"]) / 2,
        "y": (left["y"] + right["y"]) / 2,
        "z": (left.get("z", 0) + right.get("z", 0)) / 2,
        "visibility": (left.get("visibility", 0) + right.get("visibility", 0)) / 2,
    }


def _frame_metrics(frame: dict[str, Any]) -> dict[str, float | bool]:
    landmarks = frame["landmarks"]
    left_knee_angle = calculate_knee_angle(
        landmarks["left_hip"], landmarks["left_knee"], landmarks["left_ankle"]
    )
    right_knee_angle = calculate_knee_angle(
        landmarks["right_hip"], landmarks["right_knee"], landmarks["right_ankle"]
    )
    knee_angle = mean([left_knee_angle, right_knee_angle])

    mid_shoulder = _avg_point(landmarks["left_shoulder"], landmarks["right_shoulder"])
    mid_hip = _avg_point(landmarks["left_hip"], landmarks["right_hip"])
    mid_knee = _avg_point(landmarks["left_knee"], landmarks["right_knee"])
    hip_angle = calculate_hip_angle(mid_shoulder, mid_hip, mid_knee)
    trunk_angle = calculate_trunk_angle(mid_shoulder, mid_hip)

    left_valgus = landmarks["left_knee"]["x"] > (
        max(landmarks["left_hip"]["x"], landmarks["left_ankle"]["x"])
        + KNEE_VALGUS_MARGIN_NORMALIZED
    )
    right_valgus = landmarks["right_knee"]["x"] < (
        min(landmarks["right_hip"]["x"], landmarks["right_ankle"]["x"])
        - KNEE_VALGUS_MARGIN_NORMALIZED
    )

    return {
        "knee_angle": round(knee_angle, 2),
        "hip_angle": hip_angle,
        "trunk_angle": trunk_angle,
        "possible_knee_valgus": left_valgus or right_valgus,
        "low_confidence": bool(frame.get("low_confidence", False)),
    }


def create_frame_analysis(frames: list[dict[str, Any]]) -> list[FrameAnalysis]:
    """Return conservative per-frame metrics for overlays and optional API detail."""
    metrics_rows = [_frame_metrics(frame) for frame in frames]
    pose_quality = assess_pose_quality(frames)
    rep_result = count_squat_reps(
        [float(item["knee_angle"]) for item in metrics_rows],
        [float(frame.get("timestamp_sec", 0.0)) for frame in frames],
        [int(frame.get("frame_index", index)) for index, frame in enumerate(frames)],
        [bool(item["low_confidence"]) for item in metrics_rows],
        pose_quality.score,
        pose_quality.pose_detection_rate,
    )
    result: list[FrameAnalysis] = []
    for index, (frame, metrics) in enumerate(zip(frames, metrics_rows)):
        knee_angle = rep_result.smoothed_angles[index]
        next_phase = rep_result.phases[index]
        issue = None
        if bool(metrics["low_confidence"]):
            issue = "low_landmark_confidence"
        elif bool(metrics["possible_knee_valgus"]):
            issue = "possible_knee_valgus"
        elif float(metrics["trunk_angle"]) > TRUNK_LEAN_THRESHOLD_DEG:
            issue = "excessive_trunk_lean"
        result.append(
            FrameAnalysis(
                frame_index=int(frame.get("frame_index", len(result))),
                timestamp_sec=float(frame.get("timestamp_sec", 0.0)),
                knee_angle=knee_angle,
                hip_angle=float(metrics["hip_angle"]),
                trunk_angle=float(metrics["trunk_angle"]),
                phase=next_phase,
                detected_issue=issue,
            )
        )
    return result


def _sample_frame_analysis(rows: list[FrameAnalysis], limit: int) -> list[FrameAnalysis]:
    if len(rows) <= limit:
        return rows
    indexes = {round(index * (len(rows) - 1) / (limit - 1)) for index in range(limit)}
    return [rows[index] for index in sorted(indexes)]


def analyze_squat_landmarks(
    frames: list[dict[str, Any]], include_frame_data: bool = False
) -> AnalysisResponse:
    if not frames:
        return AnalysisResponse(
            status="insufficient_data",
            limitations=["No pose-detected frames were available for squat analysis."],
        )
    metrics = [_frame_metrics(frame) for frame in frames]
    raw_knee_angles = [float(item["knee_angle"]) for item in metrics]
    hip_angles = [float(item["hip_angle"]) for item in metrics]
    trunk_angles = [float(item["trunk_angle"]) for item in metrics]
    timestamps = [float(frame.get("timestamp_sec", 0.0)) for frame in frames]
    frame_indexes = [int(frame.get("frame_index", index)) for index, frame in enumerate(frames)]
    pose_quality = assess_pose_quality(frames)
    rep_result = count_squat_reps(
        raw_knee_angles,
        timestamps,
        frame_indexes,
        [bool(item["low_confidence"]) for item in metrics],
        pose_quality.score,
        pose_quality.pose_detection_rate,
    )
    knee_angles = rep_result.smoothed_angles

    depth_frames = [angle for angle in knee_angles if angle < SQUAT_DEPTH_KNEE_ANGLE_DEG]
    total_reps = rep_result.total_reps
    analysis_confidence = calculate_analysis_confidence(
        pose_quality, rep_result.confidence, knee_angles
    )
    if rep_result.confidence < 0.5:
        analysis_confidence.warnings.append(
            "Rep count confidence is low. Review camera setup and consider trimming the video to only the squat set."
        )
    input_validity = validate_squat_attempt(
        knee_angles, hip_angles, total_reps, pose_quality, frame_indexes
    )

    limitations = [
        "Rule-based prototype; results depend on camera angle, lighting, and full-body visibility.",
        "2D pose landmarks cannot fully assess joint loading or pain.",
        "Clinical decisions should be made with a licensed physiotherapist.",
    ]
    limitations.extend(warning for warning in pose_quality.warnings if warning not in limitations)

    if not input_validity.is_valid:
        analysis_confidence.score = min(analysis_confidence.score, 0.39)
        analysis_confidence.level = "low"
        for warning in input_validity.warnings:
            if warning not in analysis_confidence.warnings:
                analysis_confidence.warnings.append(warning)
        return AnalysisResponse(
            status="rejected",
            error_code="INVALID_SQUAT_VIDEO",
            message="No valid squat movement was detected.",
            total_reps=0,
            average_knee_angle=round(mean(knee_angles), 2),
            average_hip_angle=round(mean(hip_angles), 2),
            average_trunk_angle=round(mean(trunk_angles), 2),
            movement_score=None,
            detected_issues=["no_valid_squat_detected"],
            feedback=[
                "Please upload a video showing the full body performing 3–5 squat repetitions.",
                DISCLAIMER,
            ],
            summary="The recording did not pass the squat-movement validity checks, so movement quality was not scored.",
            limitations=limitations,
            ignored_partial_reps=rep_result.ignored_partial_reps,
            partial_rep_events=[event.__dict__ for event in rep_result.partial_rep_events],
            rep_count_confidence=rep_result.confidence,
            pose_quality=pose_quality,
            analysis_confidence=analysis_confidence,
            input_validity=input_validity,
            validation_warnings=input_validity.warnings,
        )

    detected_issues: list[str] = []

    # Depth is based on the smoothed minimum rather than a fragile frame ratio.
    if knee_angles and min(knee_angles) > SQUAT_DEPTH_KNEE_ANGLE_DEG:
        detected_issues.append("poor_depth")

    movement_trunk = [trunk for trunk, knee in zip(trunk_angles, knee_angles) if knee < STANDING_KNEE_ANGLE_DEG]
    if movement_trunk and mean(movement_trunk) > TRUNK_LEAN_THRESHOLD_DEG:
        detected_issues.append("excessive_trunk_lean")

    valgus_ratio = sum(bool(item["possible_knee_valgus"]) for item in metrics) / len(metrics)
    if valgus_ratio > KNEE_VALGUS_FRAME_RATIO:
        detected_issues.append("possible_knee_valgus")

    rep_minimums = [event.minimum_knee_angle for event in rep_result.rep_events]
    consistency_values = rep_minimums or depth_frames
    if len(consistency_values) > 1 and pstdev(consistency_values) > INCONSISTENT_DEPTH_STD_DEG:
        detected_issues.append("inconsistent_movement")

    low_confidence_ratio = pose_quality.low_confidence_frames / max(1, pose_quality.pose_detected_frames)
    if low_confidence_ratio > LOW_CONFIDENCE_FRAME_RATIO:
        detected_issues.append("low_landmark_confidence")

    score, score_breakdown = score_squat(
        knee_angles,
        trunk_angles,
        [bool(item["possible_knee_valgus"]) for item in metrics],
        pose_quality,
        rep_minimums,
    )
    summary = (
        f"Analyzed {len(frames)} pose-detected frames and counted {total_reps} squat rep"
        f"{'' if total_reps == 1 else 's'} with a movement score of {score}/100."
    )

    frame_analysis = create_frame_analysis(frames)
    if include_frame_data:
        from app.core.config import get_settings

        detailed_rows = _sample_frame_analysis(
            frame_analysis, get_settings().max_frame_analysis_rows
        )
    else:
        detailed_rows = None

    return AnalysisResponse(
        total_reps=total_reps,
        average_knee_angle=round(mean(knee_angles), 2),
        average_hip_angle=round(mean(hip_angles), 2),
        average_trunk_angle=round(mean(trunk_angles), 2),
        movement_score=score,
        rep_events=[event.__dict__ for event in rep_result.rep_events],
        partial_rep_events=[event.__dict__ for event in rep_result.partial_rep_events],
        rep_durations=[event.duration_sec for event in rep_result.rep_events if event.duration_sec is not None],
        ignored_partial_reps=rep_result.ignored_partial_reps,
        rep_count_confidence=rep_result.confidence,
        pose_quality=pose_quality,
        score_breakdown=score_breakdown,
        analysis_confidence=analysis_confidence,
        input_validity=input_validity,
        validation_warnings=input_validity.warnings,
        detected_issues=detected_issues,
        feedback=build_feedback(detected_issues),
        summary=summary,
        limitations=limitations,
        frame_analysis=detailed_rows,
    )
