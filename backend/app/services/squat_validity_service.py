"""Reject recordings that do not contain a sufficiently visible squat attempt."""

from __future__ import annotations

from statistics import mean

from app.core.exercise_thresholds import (
    MIN_CRITICAL_LANDMARK_VISIBILITY,
    MIN_HIP_ANGLE_RANGE_DEG,
    MIN_KNEE_ANGLE_RANGE_DEG,
    MIN_MOTION_VARIATION_DEG,
    MIN_POSE_DETECTED_FRAMES,
    MIN_POSE_DETECTION_RATE,
    MIN_VALID_REPS,
)
from app.schemas.analysis_schema import InputValidity, PoseQuality


def _range(values: list[float]) -> float:
    return max(values) - min(values) if values else 0.0


def _motion_variation(knee_angles: list[float], hip_angles: list[float]) -> float:
    if len(knee_angles) < 2 or len(hip_angles) < 2:
        return 0.0
    changes = [
        (abs(knee_angles[index] - knee_angles[index - 1]) + abs(hip_angles[index] - hip_angles[index - 1])) / 2
        for index in range(1, min(len(knee_angles), len(hip_angles)))
    ]
    return mean(changes) if changes else 0.0


def validate_squat_attempt(
    knee_angles: list[float],
    hip_angles: list[float],
    valid_reps: int,
    pose_quality: PoseQuality,
    frame_indexes: list[int] | None = None,
) -> InputValidity:
    knee_range = _range(knee_angles)
    hip_range = _range(hip_angles)
    motion_variation = _motion_variation(knee_angles, hip_angles)
    blocking_warnings: list[str] = []
    informational_warnings: list[str] = []
    active_detection_rate = pose_quality.pose_detection_rate
    if frame_indexes and len(frame_indexes) > 1:
        active_span = max(frame_indexes) - min(frame_indexes) + 1
        active_detection_rate = min(1.0, len(frame_indexes) / max(1, active_span))

    if pose_quality.pose_detected_frames < MIN_POSE_DETECTED_FRAMES:
        blocking_warnings.append(
            f"At least {MIN_POSE_DETECTED_FRAMES} pose-detected frames are required."
        )
    if active_detection_rate < MIN_POSE_DETECTION_RATE:
        blocking_warnings.append("The body was not detected consistently during the movement segment.")
    elif pose_quality.pose_detection_rate < MIN_POSE_DETECTION_RATE:
        informational_warnings.append(
            "The body was visible during the movement segment but absent from much of the full video."
        )
    if pose_quality.critical_landmark_visibility < MIN_CRITICAL_LANDMARK_VISIBILITY:
        blocking_warnings.append("The full body and key joints were not sufficiently visible.")
    if knee_range < MIN_KNEE_ANGLE_RANGE_DEG:
        blocking_warnings.append("Knee movement was too small for a squat attempt.")
    if hip_range < MIN_HIP_ANGLE_RANGE_DEG:
        blocking_warnings.append("Hip movement was too small for a squat attempt.")
    if motion_variation < MIN_MOTION_VARIATION_DEG:
        blocking_warnings.append("Video appears static or does not show enough squat movement.")
    if valid_reps < MIN_VALID_REPS:
        blocking_warnings.append("No complete squat repetition was detected.")

    warnings = blocking_warnings + informational_warnings

    return InputValidity(
        is_valid=not blocking_warnings,
        reason=None if not blocking_warnings else "no_valid_squat_detected",
        pose_detected_frames=pose_quality.pose_detected_frames,
        pose_detection_rate=round(active_detection_rate, 3),
        overall_pose_detection_rate=pose_quality.pose_detection_rate,
        critical_landmark_visibility=pose_quality.critical_landmark_visibility,
        knee_angle_range=round(knee_range, 2),
        hip_angle_range=round(hip_range, 2),
        motion_variation=round(motion_variation, 2),
        valid_reps=valid_reps,
        warnings=warnings,
    )
