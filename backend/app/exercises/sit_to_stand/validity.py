"""Conservative validity gate for sit-to-stand inputs."""

from app.schemas.analysis_schema import PoseQuality

from .schemas import SitToStandCountResult, SitToStandValidity
from .thresholds import (
    MIN_ANGLE_DELTA, MIN_CRITICAL_LANDMARK_VISIBILITY, MIN_POSE_DETECTED_FRAMES,
    MIN_POSE_DETECTION_RATE,
)


def validate_sit_to_stand(
    knee_angles: list[float], hip_angles: list[float],
    count: SitToStandCountResult, pose_quality: PoseQuality,
) -> SitToStandValidity:
    knee_range = max(knee_angles) - min(knee_angles) if knee_angles else 0.0
    hip_range = max(hip_angles) - min(hip_angles) if hip_angles else 0.0
    warnings: list[str] = []
    if pose_quality.pose_detected_frames < MIN_POSE_DETECTED_FRAMES:
        warnings.append("Too few pose-detected frames were available.")
    if pose_quality.pose_detection_rate < MIN_POSE_DETECTION_RATE:
        warnings.append("The body was absent or not detected for much of the video.")
    if pose_quality.critical_landmark_visibility < MIN_CRITICAL_LANDMARK_VISIBILITY:
        warnings.append("Hips, knees, ankles, or shoulders were not sufficiently visible.")
    if knee_range < MIN_ANGLE_DELTA or hip_range < MIN_ANGLE_DELTA:
        warnings.append("The video appears static or does not show enough sitting-to-standing motion.")
    if count.total_reps < 1:
        warnings.append("No complete sitting-to-standing-to-sitting repetition was detected.")
    valid = not warnings
    reason = None if valid else "no_valid_sit_to_stand_detected"
    return SitToStandValidity(valid, reason, round(knee_range, 2), round(hip_range, 2), count.total_reps, warnings)
