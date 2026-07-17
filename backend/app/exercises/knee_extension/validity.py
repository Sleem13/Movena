"""Fail-closed validity gate for seated knee-extension recordings."""

from app.schemas.analysis_schema import PoseQuality

from .schemas import KneeExtensionCountResult, KneeExtensionValidity
from .thresholds import MIN_ANGLE_RANGE, MIN_POSE_DETECTED_FRAMES, MIN_POSE_VISIBILITY, MIN_VALID_FRAMES_RATIO


def validate_knee_extension(
    knee_angles: list[float], count: KneeExtensionCountResult,
    pose_quality: PoseQuality, critical_visibility: float | None = None,
) -> KneeExtensionValidity:
    angle_range = max(knee_angles) - min(knee_angles) if knee_angles else 0.0
    visibility = pose_quality.critical_landmark_visibility if critical_visibility is None else critical_visibility
    warnings: list[str] = []
    if pose_quality.pose_detected_frames < MIN_POSE_DETECTED_FRAMES:
        warnings.append("The video was too short or contained too few pose-detected frames.")
    if pose_quality.pose_detection_rate < MIN_VALID_FRAMES_RATIO:
        warnings.append("The hip, knee, and ankle were not detected for enough of the recording.")
    if visibility < MIN_POSE_VISIBILITY:
        warnings.append("The selected-side hip, knee, and ankle were not sufficiently visible.")
    if angle_range < MIN_ANGLE_RANGE:
        warnings.append("The video appears static or shows insufficient knee extension range.")
    if count.total_reps < 1:
        warnings.append("No complete flexion-extension-flexion repetition was detected.")
    return KneeExtensionValidity(
        is_valid=not warnings,
        reason=None if not warnings else "no_valid_knee_extension_detected",
        knee_angle_range=round(angle_range, 2), valid_reps=count.valid_reps,
        warnings=warnings,
    )

