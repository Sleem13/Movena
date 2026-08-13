"""Rule-based video gait screen using 2D pose landmarks."""

from __future__ import annotations

from pathlib import Path
from statistics import mean, pstdev
from typing import Any

from app.exercises.base import ExerciseAnalyzer
from app.schemas.analysis_schema import (
    AnalysisConfidence,
    AnalysisResponse,
    FrameAnalysis,
    GaitMetrics,
    InputValidity,
    MLPrediction,
    RepEvent,
    ScoreBreakdown,
)
from app.services.angle_calculation_service import calculate_hip_angle, calculate_knee_angle, calculate_trunk_angle
from app.services.pose_estimation_service import extract_pose_landmarks
from app.services.pose_quality_service import assess_pose_quality

from .feedback import build_gait_feedback
from .schemas import GaitCountResult, GaitCycleEvent, GaitScore
from .thresholds import (
    ASYMMETRY_REVIEW_THRESHOLD,
    CADENCE_MAX_STEPS_PER_MIN,
    CADENCE_MIN_STEPS_PER_MIN,
    CADENCE_TARGET_HIGH,
    CADENCE_TARGET_LOW,
    MIN_CRITICAL_VISIBILITY,
    MIN_FOOT_EXCURSION,
    MIN_GAIT_CYCLES,
    MIN_KNEE_ROM_DEG,
    REFERENCE_STANCE_PERCENT,
    REFERENCE_SWING_PERCENT,
    STANCE_TOLERANCE_PERCENT,
    STRIDE_VARIABILITY_REVIEW_THRESHOLD,
)


def unavailable_ml_prediction() -> MLPrediction:
    return MLPrediction(
        enabled=False,
        model_version="not_applicable",
        warning="ML prediction is not applicable for gait screening; rule-based analysis remains primary.",
    )


def _clamp_score(value: float) -> int:
    return round(max(0.0, min(100.0, value)))


def _point_visibility(frame: dict[str, Any], side: str) -> float:
    points = frame.get("landmarks", {})
    names = (f"{side}_hip", f"{side}_knee", f"{side}_ankle", f"{side}_heel", f"{side}_foot_index")
    return min(float(points.get(name, {}).get("visibility", 0)) for name in names)


def _midpoint(first: dict[str, float], second: dict[str, float]) -> dict[str, float]:
    return {
        "x": (float(first["x"]) + float(second["x"])) / 2,
        "y": (float(first["y"]) + float(second["y"])) / 2,
        "visibility": min(float(first.get("visibility", 0)), float(second.get("visibility", 0))),
    }


def _landmark_metrics(frame: dict[str, Any]) -> dict[str, float] | None:
    points = frame.get("landmarks", {})
    required = [
        "left_shoulder",
        "right_shoulder",
        "left_hip",
        "right_hip",
        "left_knee",
        "right_knee",
        "left_ankle",
        "right_ankle",
        "left_heel",
        "right_heel",
        "left_foot_index",
        "right_foot_index",
    ]
    if any(name not in points for name in required):
        return None

    mid_hip = _midpoint(points["left_hip"], points["right_hip"])
    mid_shoulder = _midpoint(points["left_shoulder"], points["right_shoulder"])
    left_foot = _midpoint(points["left_heel"], points["left_foot_index"])
    right_foot = _midpoint(points["right_heel"], points["right_foot_index"])
    left_knee = calculate_knee_angle(points["left_hip"], points["left_knee"], points["left_ankle"])
    right_knee = calculate_knee_angle(points["right_hip"], points["right_knee"], points["right_ankle"])
    left_hip = calculate_hip_angle(points["left_shoulder"], points["left_hip"], points["left_knee"])
    right_hip = calculate_hip_angle(points["right_shoulder"], points["right_hip"], points["right_knee"])
    return {
        "left_relative_foot_x": float(left_foot["x"]) - float(mid_hip["x"]),
        "right_relative_foot_x": float(right_foot["x"]) - float(mid_hip["x"]),
        "left_knee_angle": left_knee,
        "right_knee_angle": right_knee,
        "average_knee_angle": (left_knee + right_knee) / 2,
        "average_hip_angle": (left_hip + right_hip) / 2,
        "trunk_angle": calculate_trunk_angle(mid_shoulder, mid_hip),
        "visibility": min(_point_visibility(frame, "left"), _point_visibility(frame, "right")),
    }


def _smooth(values: list[float], window: int = 5) -> list[float]:
    if len(values) < 3:
        return values
    half = window // 2
    smoothed: list[float] = []
    for index in range(len(values)):
        start = max(0, index - half)
        end = min(len(values), index + half + 1)
        smoothed.append(round(mean(values[start:end]), 4))
    return smoothed


def _local_extrema(values: list[float], mode: str) -> list[int]:
    if len(values) < 3:
        return []
    candidates: list[int] = []
    span = max(0.015, (max(values) - min(values)) * 0.18)
    for index in range(1, len(values) - 1):
        previous_value, value, next_value = values[index - 1], values[index], values[index + 1]
        if mode == "max" and value >= previous_value and value > next_value and value >= min(values) + span:
            candidates.append(index)
        if mode == "min" and value <= previous_value and value < next_value and value <= max(values) - span:
            candidates.append(index)
    deduped: list[int] = []
    min_gap = max(3, len(values) // 24)
    for index in candidates:
        if deduped and index - deduped[-1] < min_gap:
            better = values[index] > values[deduped[-1]] if mode == "max" else values[index] < values[deduped[-1]]
            if better:
                deduped[-1] = index
        else:
            deduped.append(index)
    return deduped


def _cycle_events_for_side(
    side: str,
    relative_foot_x: list[float],
    knee_angles: list[float],
    timestamps: list[float],
    indexes: list[int],
) -> tuple[list[int], list[GaitCycleEvent]]:
    smoothed = _smooth(relative_foot_x)
    strikes = _local_extrema(smoothed, "max")
    toe_offs = _local_extrema(smoothed, "min")
    cycles: list[GaitCycleEvent] = []
    for start, end in zip(strikes, strikes[1:]):
        mids = [index for index in toe_offs if start < index < end]
        if not mids:
            continue
        toe_off = min(mids, key=lambda index: smoothed[index])
        duration = timestamps[end] - timestamps[start]
        if duration <= 0:
            continue
        stance = 100 * (timestamps[toe_off] - timestamps[start]) / duration
        excursion = max(smoothed[start:end + 1]) - min(smoothed[start:end + 1])
        if excursion < MIN_FOOT_EXCURSION:
            continue
        knee_range = max(knee_angles[start:end + 1]) - min(knee_angles[start:end + 1])
        cycles.append(
            GaitCycleEvent(
                side=side,
                start_frame=indexes[start],
                toe_off_frame=indexes[toe_off],
                end_frame=indexes[end],
                duration_sec=round(duration, 3),
                stance_percent=round(stance, 1),
                swing_percent=round(100 - stance, 1),
                stride_excursion=round(excursion, 4),
                knee_range=round(knee_range, 2),
            )
        )
    return [indexes[index] for index in strikes], cycles


def count_gait_cycles(metrics: list[dict[str, float]], timestamps: list[float], indexes: list[int], quality_score: float, critical_visibility: float) -> GaitCountResult:
    left_x = [item["left_relative_foot_x"] for item in metrics]
    right_x = [item["right_relative_foot_x"] for item in metrics]
    left_knee = [item["left_knee_angle"] for item in metrics]
    right_knee = [item["right_knee_angle"] for item in metrics]
    left_steps, left_cycles = _cycle_events_for_side("left", left_x, left_knee, timestamps, indexes)
    right_steps, right_cycles = _cycle_events_for_side("right", right_x, right_knee, timestamps, indexes)
    cycles = sorted(left_cycles + right_cycles, key=lambda event: (event.start_frame, event.side))
    all_steps = sorted(left_steps + right_steps)
    durations = [event.duration_sec for event in cycles]
    phases = ["gait_cycle"]
    phase_transitions = [f"{event.side}_initial_contact:{event.start_frame}" for event in cycles]
    confidence = min(1.0, 0.42 * min(1.0, len(cycles) / 4) + 0.33 * quality_score + 0.25 * critical_visibility)
    return GaitCountResult(
        total_steps=len(all_steps),
        valid_cycles=len(cycles),
        confidence=round(confidence, 3),
        cycle_events=cycles,
        cycle_durations=durations,
        phases=phases,
        phase_transitions=phase_transitions,
        smoothed_knee_angles=_smooth([item["average_knee_angle"] for item in metrics]),
    )


def _symmetry_index(cycles: list[GaitCycleEvent]) -> float | None:
    left = [event.duration_sec for event in cycles if event.side == "left"]
    right = [event.duration_sec for event in cycles if event.side == "right"]
    if not left or not right:
        return None
    denominator = (mean(left) + mean(right)) / 2
    if denominator == 0:
        return None
    return round(abs(mean(left) - mean(right)) / denominator * 100, 1)


def _score_gait(count: GaitCountResult, pose_score: float, critical_visibility: float, cadence: float | None) -> tuple[GaitScore, GaitMetrics]:
    cycles = count.cycle_events
    stance = mean(event.stance_percent for event in cycles) if cycles else None
    swing = mean(event.swing_percent for event in cycles) if cycles else None
    durations = count.cycle_durations
    variability = round(pstdev(durations) / mean(durations), 3) if len(durations) > 1 and mean(durations) else None
    symmetry = _symmetry_index(cycles)
    knee_range = mean(event.knee_range for event in cycles) if cycles else None
    relative_stride = mean(event.stride_excursion for event in cycles) if cycles else None

    phase_score = _clamp_score(100 - abs((stance or REFERENCE_STANCE_PERCENT) - REFERENCE_STANCE_PERCENT) * 4)
    if cadence is None:
        cadence_score = 70
    elif cadence < CADENCE_MIN_STEPS_PER_MIN:
        cadence_score = _clamp_score(65 * cadence / CADENCE_MIN_STEPS_PER_MIN)
    elif cadence > CADENCE_MAX_STEPS_PER_MIN:
        cadence_score = _clamp_score(100 - (cadence - CADENCE_MAX_STEPS_PER_MIN) * 3)
    elif CADENCE_TARGET_LOW <= cadence <= CADENCE_TARGET_HIGH:
        cadence_score = 100
    else:
        cadence_score = 82
    symmetry_score = _clamp_score(100 - (symmetry or 0) * 3.2)
    consistency_score = _clamp_score(100 * (1 - (variability or 0)))
    kinematic_score = _clamp_score(100 * min(1.0, (knee_range or 0) / max(1, MIN_KNEE_ROM_DEG)))
    visibility_score = _clamp_score(55 * critical_visibility + 45 * pose_score)

    issues: list[str] = []
    if count.valid_cycles < MIN_GAIT_CYCLES:
        issues.append("insufficient_gait_cycles")
    if critical_visibility < MIN_CRITICAL_VISIBILITY:
        issues.append("poor_visibility")
    if stance is not None and abs(stance - REFERENCE_STANCE_PERCENT) > STANCE_TOLERANCE_PERCENT:
        issues.append("stance_swing_outside_reference")
    if symmetry is not None and symmetry >= ASYMMETRY_REVIEW_THRESHOLD:
        issues.append("asymmetric_timing")
    if variability is not None and variability >= STRIDE_VARIABILITY_REVIEW_THRESHOLD:
        issues.append("inconsistent_stride_timing")
    if cadence is not None and cadence < CADENCE_MIN_STEPS_PER_MIN:
        issues.append("low_cadence")
    if cadence is not None and cadence > CADENCE_MAX_STEPS_PER_MIN:
        issues.append("high_cadence")
    if knee_range is not None and knee_range < MIN_KNEE_ROM_DEG:
        issues.append("limited_knee_motion")

    total = _clamp_score(
        0.22 * phase_score
        + 0.16 * cadence_score
        + 0.20 * symmetry_score
        + 0.16 * consistency_score
        + 0.12 * kinematic_score
        + 0.14 * visibility_score
    )
    metrics = GaitMetrics(
        step_count=count.total_steps,
        gait_cycles=count.valid_cycles,
        cadence_steps_per_min=round(cadence, 1) if cadence is not None else None,
        average_cycle_duration_sec=round(mean(durations), 2) if durations else None,
        average_stance_percent=round(stance, 1) if stance is not None else None,
        average_swing_percent=round(swing, 1) if swing is not None else None,
        temporal_symmetry_index=symmetry,
        stride_time_variability=variability,
        relative_stride_excursion=round(relative_stride, 4) if relative_stride is not None else None,
        average_knee_range_deg=round(knee_range, 1) if knee_range is not None else None,
        reference_dataset_notes=[
            "Normal adult gait reference: stance is approximately 60% of the gait cycle and swing approximately 40%.",
            "Cadence, symmetry, and stride timing are 2D video-derived estimates and are not lab-grade gait-lab measurements.",
            "Public gait datasets reviewed include PhysioNet gait stride intervals, PhysioNet multimodal gait, Mendeley overground kinematics/kinetics, and open biomechanics marker datasets.",
        ],
    )
    return (
        GaitScore(total, phase_score, cadence_score, symmetry_score, consistency_score, kinematic_score, visibility_score, issues),
        metrics,
    )


class GaitAnalyzer(ExerciseAnalyzer):
    exercise_id = "walking_gait_screen"

    def analyze(self, video_path: Path, options: dict[str, Any] | None = None) -> AnalysisResponse:
        options = options or {}
        return self.analyze_landmarks(
            extract_pose_landmarks(video_path),
            include_frame_data=bool(options.get("include_frame_data")),
        )

    def count_reps(self, *args: Any, **kwargs: Any) -> GaitCountResult:
        return count_gait_cycles(*args, **kwargs)

    def validate_input(self, *args: Any, **kwargs: Any) -> bool:
        return True

    def score_movement(self, *args: Any, **kwargs: Any):
        return _score_gait(*args, **kwargs)

    def generate_feedback(self, *args: Any, **kwargs: Any) -> list[str]:
        return build_gait_feedback(*args, **kwargs)

    def _empty_rejection(self) -> AnalysisResponse:
        return AnalysisResponse(
            exercise=self.exercise_id,
            exercise_id=self.exercise_id,
            exercise_name="Walking Gait Screen",
            status="rejected",
            error_code="INVALID_GAIT_VIDEO",
            message="No valid walking gait cycle was detected.",
            movement_score=None,
            valid_reps=0,
            detected_issues=["no_valid_gait_detected"],
            feedback=build_gait_feedback(["no_valid_gait_detected"]),
            ml_prediction=unavailable_ml_prediction(),
            limitations=["No usable pose-detected frames were available."],
        )

    def analyze_landmarks(self, frames: list[dict[str, Any]], include_frame_data: bool = False) -> AnalysisResponse:
        if not frames:
            return self._empty_rejection()

        usable: list[tuple[dict[str, Any], dict[str, float]]] = []
        for frame in frames:
            metrics = _landmark_metrics(frame)
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
        duration = max(timestamps) - min(timestamps) if len(timestamps) > 1 else 0
        count = count_gait_cycles(metric_rows, timestamps, indexes, quality.score, critical_visibility)
        cadence = (count.total_steps / duration * 60) if duration > 0 and count.total_steps else None
        score, gait_metrics = _score_gait(count, quality.score, critical_visibility, cadence)
        is_valid = count.valid_cycles >= MIN_GAIT_CYCLES and critical_visibility >= MIN_CRITICAL_VISIBILITY
        input_validity = InputValidity(
            is_valid=is_valid,
            reason=None if is_valid else "At least two clear same-side gait cycles with visible lower-limb landmarks are required.",
            pose_detected_frames=quality.pose_detected_frames,
            pose_detection_rate=quality.pose_detection_rate,
            overall_pose_detection_rate=quality.pose_detection_rate,
            critical_landmark_visibility=critical_visibility,
            knee_angle_range=round(max(item["average_knee_angle"] for item in metric_rows) - min(item["average_knee_angle"] for item in metric_rows), 2),
            hip_angle_range=round(max(item["average_hip_angle"] for item in metric_rows) - min(item["average_hip_angle"] for item in metric_rows), 2),
            motion_variation=round(max(item["left_relative_foot_x"] for item in metric_rows) - min(item["left_relative_foot_x"] for item in metric_rows), 3),
            valid_reps=count.valid_cycles,
            warnings=list(score.issues),
        )
        confidence_score = round(min(1.0, 0.55 * count.confidence + 0.25 * quality.score + 0.20 * critical_visibility), 3)
        confidence = AnalysisConfidence(
            score=confidence_score if is_valid else min(0.39, confidence_score),
            level="high" if is_valid and confidence_score >= 0.8 else "medium" if is_valid and confidence_score >= 0.6 else "low",
            reasons=[
                f"Detected {count.valid_cycles} complete same-side gait cycle{'s' if count.valid_cycles != 1 else ''}.",
                f"Lower-limb landmark visibility was {round(critical_visibility * 100)}%.",
            ],
            warnings=list(score.issues),
        )
        common = dict(
            exercise=self.exercise_id,
            exercise_id=self.exercise_id,
            exercise_name="Walking Gait Screen",
            total_reps=count.total_steps,
            valid_reps=count.valid_cycles,
            average_knee_angle=round(mean(item["average_knee_angle"] for item in metric_rows), 2),
            average_hip_angle=round(mean(item["average_hip_angle"] for item in metric_rows), 2),
            average_trunk_angle=round(mean(item["trunk_angle"] for item in metric_rows), 2),
            rep_events=[
                RepEvent(
                    start_frame=event.start_frame,
                    standing_frame=event.toe_off_frame,
                    end_frame=event.end_frame,
                    duration_sec=event.duration_sec,
                    minimum_knee_angle=None,
                    maximum_knee_angle=event.knee_range,
                )
                for event in count.cycle_events
            ],
            rep_durations=count.cycle_durations,
            ignored_partial_reps=0,
            rep_count_confidence=count.confidence,
            phase_transitions=count.phase_transitions,
            pose_quality=quality,
            analysis_confidence=confidence,
            input_validity=input_validity,
            validation_warnings=list(score.issues),
            ml_prediction=unavailable_ml_prediction(),
            gait_metrics=gait_metrics,
        )
        limitations = [
            "Rule-based gait screening is an educational MVP and is not clinically validated.",
            "Monocular 2D video cannot directly measure ground reaction force, joint moments, center of pressure, true step length, or walking speed without calibration.",
            "The stance/swing and cadence values are estimates from visible pose timing; treadmill, assistive-device, turn, and occlusion videos may be unreliable.",
            "AI feedback supports gait monitoring and does not replace physiotherapist assessment.",
        ]
        if not is_valid:
            return AnalysisResponse(
                **common,
                status="rejected",
                error_code="INVALID_GAIT_VIDEO",
                message="No valid walking gait cycle was detected.",
                movement_score=None,
                score_breakdown=None,
                detected_issues=score.issues or ["no_valid_gait_detected"],
                feedback=build_gait_feedback(score.issues or ["no_valid_gait_detected"]),
                summary="The recording did not contain enough clear same-side gait cycles for a gait screen.",
                limitations=limitations,
            )

        frame_rows = [
            FrameAnalysis(
                frame_index=indexes[index],
                timestamp_sec=timestamps[index],
                knee_angle=round(count.smoothed_knee_angles[index], 2),
                hip_angle=round(metric_rows[index]["average_hip_angle"], 2),
                trunk_angle=round(metric_rows[index]["trunk_angle"], 2),
                phase="walking",
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
                gait_phase_score=score.gait_phase_score,
                cadence_score=score.cadence_score,
                symmetry_score=score.symmetry_score,
                stride_consistency_score=score.stride_consistency_score,
                kinematic_range_score=score.kinematic_range_score,
                posture_visibility_score=score.posture_visibility_score,
                pose_confidence_score=score.posture_visibility_score,
            ),
            detected_issues=score.issues,
            feedback=build_gait_feedback(score.issues),
            summary=f"Analyzed {len(usable_frames)} pose-detected frames and estimated {count.total_steps} foot-contact events across {count.valid_cycles} complete gait cycles.",
            limitations=limitations,
            frame_analysis=frame_rows if include_frame_data else None,
        )


gait_analyzer = GaitAnalyzer()

