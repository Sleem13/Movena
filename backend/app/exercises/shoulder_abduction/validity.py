"""Fail-closed validity gate for shoulder-abduction recordings."""

from app.schemas.analysis_schema import PoseQuality

from .schemas import ShoulderAbductionCountResult, ShoulderAbductionValidity
from .thresholds import MIN_ANGLE_RANGE, MIN_POSE_DETECTED_FRAMES, MIN_POSE_VISIBILITY, MIN_VALID_FRAMES_RATIO


def validate_shoulder_abduction(angles: list[float], count: ShoulderAbductionCountResult, pose_quality: PoseQuality, critical_visibility: float | None = None) -> ShoulderAbductionValidity:
    angle_range = max(angles) - min(angles) if angles else 0.0
    visibility = pose_quality.critical_landmark_visibility if critical_visibility is None else critical_visibility
    warnings = []
    if pose_quality.pose_detected_frames < MIN_POSE_DETECTED_FRAMES:
        warnings.append("The video was too short or contained too few pose-detected frames.")
    if pose_quality.pose_detection_rate < MIN_VALID_FRAMES_RATIO:
        warnings.append("The shoulder, elbow, wrist, and hip were not detected for enough of the recording.")
    if visibility < MIN_POSE_VISIBILITY:
        warnings.append("The selected-side shoulder, elbow, wrist, and hip were not sufficiently visible.")
    if angle_range < MIN_ANGLE_RANGE:
        warnings.append("The video appears static or shows insufficient shoulder abduction range.")
    if count.total_reps < 1:
        warnings.append("No complete lowered-raised-lowered repetition was detected.")
    return ShoulderAbductionValidity(not warnings, None if not warnings else "no_valid_shoulder_abduction_detected", round(angle_range, 2), count.valid_reps, warnings)
