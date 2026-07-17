"""Fail-closed validity gate for standing hip-abduction recordings."""

from app.schemas.analysis_schema import PoseQuality

from .schemas import HipAbductionCountResult, HipAbductionValidity
from .thresholds import MIN_ANGLE_RANGE, MIN_POSE_DETECTED_FRAMES, MIN_POSE_VISIBILITY, MIN_VALID_FRAMES_RATIO


def validate_hip_abduction(angles: list[float], count: HipAbductionCountResult, pose_quality: PoseQuality, critical_visibility: float | None = None) -> HipAbductionValidity:
    angle_range = max(angles) - min(angles) if angles else 0.0
    visibility = pose_quality.critical_landmark_visibility if critical_visibility is None else critical_visibility
    warnings = []
    if pose_quality.pose_detected_frames < MIN_POSE_DETECTED_FRAMES:
        warnings.append("The video was too short or contained too few pose-detected frames.")
    if pose_quality.pose_detection_rate < MIN_VALID_FRAMES_RATIO:
        warnings.append("The pelvis, hip, knee, and ankle were not detected for enough of the recording.")
    if visibility < MIN_POSE_VISIBILITY:
        warnings.append("The selected-side hip, knee, ankle, and trunk reference were not sufficiently visible.")
    if angle_range < MIN_ANGLE_RANGE:
        warnings.append("The video appears static or shows insufficient hip abduction range.")
    if count.total_reps < 1:
        warnings.append("No complete neutral-abducted-neutral repetition was detected.")
    return HipAbductionValidity(not warnings, None if not warnings else "no_valid_hip_abduction_detected", round(angle_range, 2), count.valid_reps, warnings)
