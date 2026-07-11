from statistics import mean, pstdev
from typing import Any

from app.schemas.analysis_schema import AnalysisResponse, FrameAnalysis
from app.core.exercise_thresholds import (
    INCONSISTENT_DEPTH_STD_DEG,
    ISSUE_SCORE_DEDUCTIONS,
    KNEE_VALGUS_FRAME_RATIO,
    KNEE_VALGUS_MARGIN_NORMALIZED,
    LOW_CONFIDENCE_FRAME_RATIO,
    POOR_DEPTH_FRAME_RATIO,
    SQUAT_DEPTH_KNEE_ANGLE_DEG,
    STANDING_KNEE_ANGLE_DEG,
    TRUNK_LEAN_THRESHOLD_DEG,
)
from app.services.angle_calculation_service import (
    calculate_hip_angle,
    calculate_knee_angle,
    calculate_trunk_angle,
)
from app.services.feedback_service import build_feedback

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


def _phase_for_angle(angle: float, current_phase: str) -> str:
    if angle < SQUAT_DEPTH_KNEE_ANGLE_DEG:
        return "depth"
    if angle > STANDING_KNEE_ANGLE_DEG:
        return "standing"
    return "descent" if current_phase == "standing" else "ascent"


def create_frame_analysis(frames: list[dict[str, Any]]) -> list[FrameAnalysis]:
    """Return conservative per-frame metrics for overlays and optional API detail."""
    result: list[FrameAnalysis] = []
    phase = "standing"
    for frame in frames:
        metrics = _frame_metrics(frame)
        knee_angle = float(metrics["knee_angle"])
        next_phase = _phase_for_angle(knee_angle, phase)
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
        phase = next_phase
    return result


def _sample_frame_analysis(rows: list[FrameAnalysis], limit: int) -> list[FrameAnalysis]:
    if len(rows) <= limit:
        return rows
    indexes = {round(index * (len(rows) - 1) / (limit - 1)) for index in range(limit)}
    return [rows[index] for index in sorted(indexes)]


def _count_reps(knee_angles: list[float]) -> int:
    reps = 0
    phase = "standing"

    for angle in knee_angles:
        if phase == "standing" and angle < SQUAT_DEPTH_KNEE_ANGLE_DEG:
            phase = "depth"
        elif phase == "depth" and angle > STANDING_KNEE_ANGLE_DEG:
            reps += 1
            phase = "standing"

    return reps


def analyze_squat_landmarks(
    frames: list[dict[str, Any]], include_frame_data: bool = False
) -> AnalysisResponse:
    metrics = [_frame_metrics(frame) for frame in frames]
    knee_angles = [float(item["knee_angle"]) for item in metrics]
    hip_angles = [float(item["hip_angle"]) for item in metrics]
    trunk_angles = [float(item["trunk_angle"]) for item in metrics]

    squat_frames = [angle for angle in knee_angles if angle < STANDING_KNEE_ANGLE_DEG]
    depth_frames = [angle for angle in knee_angles if angle < SQUAT_DEPTH_KNEE_ANGLE_DEG]
    total_reps = _count_reps(knee_angles)
    detected_issues: list[str] = []

    # Short videos may only include a few bottom-position frames, so keep this conservative.
    if squat_frames and len(depth_frames) / len(squat_frames) < POOR_DEPTH_FRAME_RATIO:
        detected_issues.append("poor_depth")
    elif not depth_frames:
        detected_issues.append("poor_depth")

    if trunk_angles and mean(trunk_angles) > TRUNK_LEAN_THRESHOLD_DEG:
        detected_issues.append("excessive_trunk_lean")

    valgus_ratio = sum(bool(item["possible_knee_valgus"]) for item in metrics) / len(metrics)
    if valgus_ratio > KNEE_VALGUS_FRAME_RATIO:
        detected_issues.append("possible_knee_valgus")

    if len(depth_frames) > 1 and pstdev(depth_frames) > INCONSISTENT_DEPTH_STD_DEG:
        detected_issues.append("inconsistent_movement")

    low_confidence_ratio = sum(bool(item["low_confidence"]) for item in metrics) / len(metrics)
    if low_confidence_ratio > LOW_CONFIDENCE_FRAME_RATIO:
        detected_issues.append("low_landmark_confidence")

    score = 100
    for issue in detected_issues:
        score -= ISSUE_SCORE_DEDUCTIONS.get(issue, 0)
    score = max(0, min(100, score))

    limitations = [
        "Rule-based prototype; results depend on camera angle, lighting, and full-body visibility.",
        "2D pose landmarks cannot fully assess joint loading or pain.",
        "Clinical decisions should be made with a licensed physiotherapist.",
    ]

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
        detected_issues=detected_issues,
        feedback=build_feedback(detected_issues),
        summary=summary,
        limitations=limitations,
        frame_analysis=detailed_rows,
    )
