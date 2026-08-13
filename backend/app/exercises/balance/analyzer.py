"""Rule-based static balance screen using 2D pose landmarks."""

from __future__ import annotations

import math
from pathlib import Path
from statistics import mean, pstdev
from typing import Any

from app.exercises.base import ExerciseAnalyzer
from app.schemas.analysis_schema import (
    AnalysisConfidence,
    AnalysisResponse,
    BalanceMetrics,
    FrameAnalysis,
    InputValidity,
    MLPrediction,
    ScoreBreakdown,
)
from app.services.angle_calculation_service import calculate_knee_angle, calculate_trunk_angle
from app.services.pose_estimation_service import extract_pose_landmarks
from app.services.pose_quality_service import assess_pose_quality

from .feedback import build_balance_feedback
from .schemas import BalanceScore
from .thresholds import (
    FOOT_ADJUSTMENT_REVIEW,
    KNEE_VARIABILITY_REVIEW_DEG,
    MIN_BALANCE_DURATION_SEC,
    MIN_CRITICAL_VISIBILITY,
    PELVIS_TILT_REVIEW,
    SINGLE_LEG_LIFT_THRESHOLD,
    SWAY_MAX_REVIEW,
    SWAY_RMS_REVIEW,
    SWAY_VELOCITY_REVIEW,
    TARGET_BALANCE_DURATION_SEC,
    TRUNK_LEAN_REVIEW_DEG,
)


def unavailable_ml_prediction() -> MLPrediction:
    return MLPrediction(
        enabled=False,
        model_version="not_applicable",
        warning="ML prediction is not applicable for balance screening; rule-based analysis remains primary.",
    )


def _clamp_score(value: float) -> int:
    return round(max(0.0, min(100.0, value)))


def _midpoint(first: dict[str, float], second: dict[str, float]) -> dict[str, float]:
    return {
        "x": (float(first["x"]) + float(second["x"])) / 2,
        "y": (float(first["y"]) + float(second["y"])) / 2,
        "visibility": min(float(first.get("visibility", 0)), float(second.get("visibility", 0))),
    }


def _distance(first: tuple[float, float], second: tuple[float, float]) -> float:
    return math.hypot(first[0] - second[0], first[1] - second[1])


def _point_visibility(frame: dict[str, Any]) -> float:
    points = frame.get("landmarks", {})
    names = (
        "left_shoulder", "right_shoulder", "left_hip", "right_hip",
        "left_knee", "right_knee", "left_ankle", "right_ankle",
        "left_heel", "right_heel", "left_foot_index", "right_foot_index",
    )
    return min(float(points.get(name, {}).get("visibility", 0)) for name in names)


def _frame_metrics(frame: dict[str, Any]) -> dict[str, float] | None:
    points = frame.get("landmarks", {})
    required = (
        "left_shoulder", "right_shoulder", "left_hip", "right_hip",
        "left_knee", "right_knee", "left_ankle", "right_ankle",
        "left_heel", "right_heel", "left_foot_index", "right_foot_index",
    )
    if any(name not in points for name in required):
        return None

    shoulder_mid = _midpoint(points["left_shoulder"], points["right_shoulder"])
    hip_mid = _midpoint(points["left_hip"], points["right_hip"])
    left_foot = _midpoint(points["left_heel"], points["left_foot_index"])
    right_foot = _midpoint(points["right_heel"], points["right_foot_index"])
    support_mid = _midpoint(left_foot, right_foot)
    body_height = max(
        0.1,
        abs(float(shoulder_mid["y"]) - max(float(points["left_ankle"]["y"]), float(points["right_ankle"]["y"]))),
    )
    left_knee = calculate_knee_angle(points["left_hip"], points["left_knee"], points["left_ankle"])
    right_knee = calculate_knee_angle(points["right_hip"], points["right_knee"], points["right_ankle"])
    foot_height_delta = abs(float(left_foot["y"]) - float(right_foot["y"]))
    support_base_width = abs(float(left_foot["x"]) - float(right_foot["x"])) / body_height
    return {
        "com_proxy_x": (float(shoulder_mid["x"]) * 0.35 + float(hip_mid["x"]) * 0.65),
        "com_proxy_y": (float(shoulder_mid["y"]) * 0.35 + float(hip_mid["y"]) * 0.65),
        "support_x": float(support_mid["x"]),
        "support_y": float(support_mid["y"]),
        "body_height": body_height,
        "trunk_angle": calculate_trunk_angle(shoulder_mid, hip_mid),
        "pelvis_tilt": abs(float(points["left_hip"]["y"]) - float(points["right_hip"]["y"])) / body_height,
        "left_knee_angle": left_knee,
        "right_knee_angle": right_knee,
        "average_knee_angle": (left_knee + right_knee) / 2,
        "foot_height_delta": foot_height_delta / body_height,
        "left_foot_x": float(left_foot["x"]),
        "right_foot_x": float(right_foot["x"]),
        "support_base_width": support_base_width,
        "visibility": _point_visibility(frame),
    }


def _balance_mode(metrics: list[dict[str, float]]) -> str:
    lifted = mean(item["foot_height_delta"] for item in metrics)
    base_width = mean(item["support_base_width"] for item in metrics)
    if lifted >= SINGLE_LEG_LIFT_THRESHOLD:
        return "single_leg_or_unilateral_stance"
    if base_width <= 0.12:
        return "narrow_or_tandem_stance"
    return "quiet_standing"


def _sway_metrics(metrics: list[dict[str, float]], timestamps: list[float]) -> BalanceMetrics:
    rel = [
        (
            (item["com_proxy_x"] - item["support_x"]) / item["body_height"],
            (item["com_proxy_y"] - item["support_y"]) / item["body_height"],
        )
        for item in metrics
    ]
    center = (mean(value[0] for value in rel), mean(value[1] for value in rel))
    distances = [_distance(value, center) for value in rel]
    duration = max(timestamps) - min(timestamps) if len(timestamps) > 1 else 0.0
    path = sum(_distance(rel[index], rel[index - 1]) for index in range(1, len(rel)))
    foot_adjustment = max(
        max(item["left_foot_x"] for item in metrics) - min(item["left_foot_x"] for item in metrics),
        max(item["right_foot_x"] for item in metrics) - min(item["right_foot_x"] for item in metrics),
    ) / max(0.1, mean(item["body_height"] for item in metrics))
    return BalanceMetrics(
        hold_duration_sec=round(duration, 2),
        balance_mode=_balance_mode(metrics),
        sway_rms=round(math.sqrt(mean(value * value for value in distances)), 4) if distances else None,
        sway_max=round(max(distances), 4) if distances else None,
        sway_path=round(path, 4),
        sway_velocity=round(path / duration, 4) if duration > 0 else None,
        average_trunk_lean_deg=round(mean(item["trunk_angle"] for item in metrics), 2),
        max_trunk_lean_deg=round(max(item["trunk_angle"] for item in metrics), 2),
        pelvis_tilt_mean=round(mean(item["pelvis_tilt"] for item in metrics), 4),
        knee_angle_variability_deg=round(pstdev(item["average_knee_angle"] for item in metrics), 2) if len(metrics) > 1 else 0.0,
        support_base_width=round(mean(item["support_base_width"] for item in metrics), 4),
        foot_adjustment_index=round(foot_adjustment, 4),
        reference_dataset_notes=[
            "Force-plate posturography commonly quantifies balance through center-of-pressure/body-sway movement during quiet standing.",
            "This MVP uses 2D pose center-of-body and support-base proxies, not true center of pressure, center of mass, vestibular function, or fall-risk classification.",
            "Public balance datasets reviewed include KINECAL, PhysioNet body-sway force-plate data, and published postural-sway normative datasets.",
        ],
    )


def _score_balance(metrics: BalanceMetrics, critical_visibility: float, pose_score: float) -> BalanceScore:
    duration_score = _clamp_score(100 * (metrics.hold_duration_sec or 0) / TARGET_BALANCE_DURATION_SEC)
    sway_rms = metrics.sway_rms or 0.0
    sway_max = metrics.sway_max or 0.0
    sway_velocity = metrics.sway_velocity or 0.0
    sway_score = _clamp_score(100 - 45 * (sway_rms / SWAY_RMS_REVIEW) - 25 * (sway_max / SWAY_MAX_REVIEW) - 30 * (sway_velocity / SWAY_VELOCITY_REVIEW))
    trunk_score = _clamp_score(100 - 100 * (metrics.max_trunk_lean_deg or 0) / max(1, TRUNK_LEAN_REVIEW_DEG * 1.8))
    pelvis_score = _clamp_score(100 - 100 * (metrics.pelvis_tilt_mean or 0) / max(0.001, PELVIS_TILT_REVIEW * 2))
    knee_score = _clamp_score(100 - 100 * (metrics.knee_angle_variability_deg or 0) / max(1, KNEE_VARIABILITY_REVIEW_DEG * 2))
    visibility_score = _clamp_score(55 * critical_visibility + 45 * pose_score)
    issues: list[str] = []
    if (metrics.hold_duration_sec or 0) < MIN_BALANCE_DURATION_SEC:
        issues.append("short_balance_hold")
    if critical_visibility < MIN_CRITICAL_VISIBILITY:
        issues.append("poor_visibility")
    if sway_rms >= SWAY_RMS_REVIEW or sway_max >= SWAY_MAX_REVIEW:
        issues.append("excessive_postural_sway")
    if sway_velocity >= SWAY_VELOCITY_REVIEW:
        issues.append("high_sway_velocity")
    if (metrics.max_trunk_lean_deg or 0) >= TRUNK_LEAN_REVIEW_DEG:
        issues.append("possible_trunk_lean")
    if (metrics.pelvis_tilt_mean or 0) >= PELVIS_TILT_REVIEW:
        issues.append("possible_pelvic_drop_or_hike")
    if (metrics.knee_angle_variability_deg or 0) >= KNEE_VARIABILITY_REVIEW_DEG:
        issues.append("variable_stance_knee")
    if (metrics.foot_adjustment_index or 0) >= FOOT_ADJUSTMENT_REVIEW:
        issues.append("foot_adjustment_detected")
    total = _clamp_score(
        0.20 * duration_score
        + 0.27 * sway_score
        + 0.15 * trunk_score
        + 0.13 * pelvis_score
        + 0.10 * knee_score
        + 0.15 * visibility_score
    )
    return BalanceScore(total, duration_score, sway_score, trunk_score, pelvis_score, knee_score, visibility_score, issues)


class BalanceAnalyzer(ExerciseAnalyzer):
    exercise_id = "balance"

    def analyze(self, video_path: Path, options: dict[str, Any] | None = None) -> AnalysisResponse:
        options = options or {}
        return self.analyze_landmarks(
            extract_pose_landmarks(video_path),
            include_frame_data=bool(options.get("include_frame_data")),
        )

    def count_reps(self, *args: Any, **kwargs: Any) -> int:
        return 0

    def validate_input(self, *args: Any, **kwargs: Any) -> bool:
        return True

    def score_movement(self, *args: Any, **kwargs: Any) -> BalanceScore:
        return _score_balance(*args, **kwargs)

    def generate_feedback(self, *args: Any, **kwargs: Any) -> list[str]:
        return build_balance_feedback(*args, **kwargs)

    def _empty_rejection(self) -> AnalysisResponse:
        return AnalysisResponse(
            exercise=self.exercise_id,
            exercise_id=self.exercise_id,
            exercise_name="Static Balance Screen",
            status="rejected",
            error_code="INVALID_BALANCE_VIDEO",
            message="No valid static balance hold was detected.",
            movement_score=None,
            valid_reps=0,
            detected_issues=["no_valid_balance_detected"],
            feedback=build_balance_feedback(["no_valid_balance_detected"]),
            ml_prediction=unavailable_ml_prediction(),
            limitations=["No usable pose-detected frames were available."],
        )

    def analyze_landmarks(self, frames: list[dict[str, Any]], include_frame_data: bool = False) -> AnalysisResponse:
        if not frames:
            return self._empty_rejection()
        usable: list[tuple[dict[str, Any], dict[str, float]]] = []
        for frame in frames:
            metrics = _frame_metrics(frame)
            if metrics is not None:
                usable.append((frame, metrics))
        if not usable:
            return self._empty_rejection()

        usable_frames = [item[0] for item in usable]
        metric_rows = [item[1] for item in usable]
        timestamps = [float(frame.get("timestamp_sec", index / 30)) for index, frame in enumerate(usable_frames)]
        indexes = [int(frame.get("frame_index", index)) for index, frame in enumerate(usable_frames)]
        quality = assess_pose_quality(frames)
        critical_visibility = round(mean(item["visibility"] for item in metric_rows), 3)
        balance_metrics = _sway_metrics(metric_rows, timestamps)
        score = _score_balance(balance_metrics, critical_visibility, quality.score)
        is_valid = (
            (balance_metrics.hold_duration_sec or 0) >= MIN_BALANCE_DURATION_SEC
            and critical_visibility >= MIN_CRITICAL_VISIBILITY
        )
        input_validity = InputValidity(
            is_valid=is_valid,
            reason=None if is_valid else "A clear static balance hold of at least three seconds is required.",
            pose_detected_frames=quality.pose_detected_frames,
            pose_detection_rate=quality.pose_detection_rate,
            overall_pose_detection_rate=quality.pose_detection_rate,
            critical_landmark_visibility=critical_visibility,
            knee_angle_range=round(max(item["average_knee_angle"] for item in metric_rows) - min(item["average_knee_angle"] for item in metric_rows), 2),
            hip_angle_range=round(max(item["pelvis_tilt"] for item in metric_rows) - min(item["pelvis_tilt"] for item in metric_rows), 4),
            motion_variation=balance_metrics.sway_max or 0,
            valid_reps=1 if is_valid else 0,
            warnings=list(score.issues),
        )
        confidence_score = round(min(1.0, 0.45 * quality.score + 0.30 * critical_visibility + 0.25 * min(1.0, (balance_metrics.hold_duration_sec or 0) / TARGET_BALANCE_DURATION_SEC)), 3)
        confidence = AnalysisConfidence(
            score=confidence_score if is_valid else min(0.39, confidence_score),
            level="high" if is_valid and confidence_score >= 0.8 else "medium" if is_valid and confidence_score >= 0.6 else "low",
            reasons=[
                f"Detected a {balance_metrics.hold_duration_sec}-second visible balance hold.",
                f"Critical landmark visibility was {round(critical_visibility * 100)}%.",
            ],
            warnings=list(score.issues),
        )
        common = dict(
            exercise=self.exercise_id,
            exercise_id=self.exercise_id,
            exercise_name="Static Balance Screen",
            total_reps=0,
            valid_reps=1 if is_valid else 0,
            average_knee_angle=round(mean(item["average_knee_angle"] for item in metric_rows), 2),
            average_hip_angle=0,
            average_trunk_angle=balance_metrics.average_trunk_lean_deg or 0,
            rep_events=[],
            rep_durations=[],
            ignored_partial_reps=0,
            rep_count_confidence=confidence.score,
            phase_transitions=[f"balance_hold:{indexes[0]}-{indexes[-1]}"],
            pose_quality=quality,
            analysis_confidence=confidence,
            input_validity=input_validity,
            validation_warnings=list(score.issues),
            ml_prediction=unavailable_ml_prediction(),
            balance_metrics=balance_metrics,
        )
        limitations = [
            "Rule-based static balance screening is an educational MVP and is not clinically validated.",
            "Monocular 2D video does not measure true center of pressure, vestibular function, proprioception, reaction to perturbation, fall risk, or treatment suitability.",
            "Use a safe support surface nearby and interpret sway estimates cautiously when the camera moves, the person turns, or feet are occluded.",
            "AI feedback supports balance monitoring and does not replace physiotherapist assessment.",
        ]
        if not is_valid:
            return AnalysisResponse(
                **common,
                status="rejected",
                error_code="INVALID_BALANCE_VIDEO",
                message="No valid static balance hold was detected.",
                movement_score=None,
                score_breakdown=None,
                detected_issues=score.issues or ["no_valid_balance_detected"],
                feedback=build_balance_feedback(score.issues or ["no_valid_balance_detected"]),
                summary="The recording did not contain a long enough clear static balance hold.",
                limitations=limitations,
            )

        frame_rows = [
            FrameAnalysis(
                frame_index=indexes[index],
                timestamp_sec=timestamps[index],
                knee_angle=round(metric_rows[index]["average_knee_angle"], 2),
                hip_angle=0,
                trunk_angle=round(metric_rows[index]["trunk_angle"], 2),
                phase="balance_hold",
                detected_issue="poor_visibility" if metric_rows[index]["visibility"] < MIN_CRITICAL_VISIBILITY else None,
            )
            for index in range(len(usable_frames))
        ]
        if include_frame_data and len(frame_rows) > 300:
            step = max(1, len(frame_rows) // 300)
            frame_rows = frame_rows[::step][:300]
        return AnalysisResponse(
            **common,
            status="success",
            movement_score=score.total,
            score_breakdown=ScoreBreakdown(
                hold_duration_score=score.hold_duration_score,
                sway_control_score=score.sway_control_score,
                trunk_control_score=score.trunk_control_score,
                pelvis_control_score=score.pelvis_control_score,
                knee_stability_score=score.knee_stability_score,
                posture_visibility_score=score.posture_visibility_score,
                pose_confidence_score=score.posture_visibility_score,
            ),
            detected_issues=score.issues,
            feedback=build_balance_feedback(score.issues),
            summary=f"Analyzed {len(usable_frames)} pose-detected frames and estimated a {balance_metrics.hold_duration_sec}-second {balance_metrics.balance_mode.replace('_', ' ')} hold.",
            limitations=limitations,
            frame_analysis=frame_rows if include_frame_data else None,
        )


balance_analyzer = BalanceAnalyzer()

