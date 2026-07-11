"""Clinically reviewable constants for the rule-based squat prototype."""

STANDING_KNEE_ANGLE_DEG = 160.0
SQUAT_DEPTH_KNEE_ANGLE_DEG = 110.0
TRUNK_LEAN_THRESHOLD_DEG = 35.0
KNEE_VALGUS_MARGIN_NORMALIZED = 0.035
POOR_DEPTH_FRAME_RATIO = 0.25
KNEE_VALGUS_FRAME_RATIO = 0.25
LOW_CONFIDENCE_FRAME_RATIO = 0.40
INCONSISTENT_DEPTH_STD_DEG = 18.0

ISSUE_SCORE_DEDUCTIONS = {
    "poor_depth": 20,
    "excessive_trunk_lean": 20,
    "possible_knee_valgus": 20,
    "inconsistent_movement": 10,
    "low_landmark_confidence": 10,
}
