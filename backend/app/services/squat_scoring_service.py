"""Explainable squat sub-scores kept separate from confidence."""

from __future__ import annotations

from statistics import mean, pstdev

from app.core.exercise_thresholds import SQUAT_DEPTH_KNEE_ANGLE_DEG, TRUNK_LEAN_THRESHOLD_DEG
from app.schemas.analysis_schema import PoseQuality, ScoreBreakdown


WEIGHTS = {
    "depth_score": 0.30,
    "knee_alignment_score": 0.25,
    "trunk_control_score": 0.20,
    "consistency_score": 0.15,
    "pose_confidence_score": 0.10,
}


def score_squat(
    knee_angles: list[float],
    trunk_angles: list[float],
    valgus_flags: list[bool],
    pose_quality: PoseQuality,
    rep_minimum_angles: list[float] | None = None,
) -> tuple[int, ScoreBreakdown]:
    minimum = min(rep_minimum_angles or knee_angles) if knee_angles else 180.0
    depth = 100 if minimum <= SQUAT_DEPTH_KNEE_ANGLE_DEG else max(
        0, round(100 - ((minimum - SQUAT_DEPTH_KNEE_ANGLE_DEG) * 2))
    )

    valgus_ratio = sum(valgus_flags) / len(valgus_flags) if valgus_flags else 0.0
    evidence_factor = 1.0 if pose_quality.camera_view == "front_or_oblique" else 0.35
    evidence_factor *= 1.0 if pose_quality.score >= 0.60 else 0.5
    knee_alignment = round(max(0, 100 - (valgus_ratio * 100 * evidence_factor)))

    movement_trunk = [
        trunk for trunk, knee in zip(trunk_angles, knee_angles) if knee < 160
    ] or trunk_angles
    average_trunk = mean(movement_trunk) if movement_trunk else 0.0
    trunk_control = round(max(0, 100 - max(0, average_trunk - TRUNK_LEAN_THRESHOLD_DEG) * 2.5))

    consistency_values = rep_minimum_angles or [
        angle for angle in knee_angles if angle <= SQUAT_DEPTH_KNEE_ANGLE_DEG + 15
    ]
    variability = pstdev(consistency_values) if len(consistency_values) > 1 else 0.0
    consistency = round(max(0, 100 - (variability * 3)))
    pose_score = round(pose_quality.score * 100)

    breakdown = ScoreBreakdown(
        depth_score=depth,
        knee_alignment_score=knee_alignment,
        trunk_control_score=trunk_control,
        consistency_score=consistency,
        pose_confidence_score=pose_score,
    )
    weighted = sum(getattr(breakdown, key) * weight for key, weight in WEIGHTS.items())
    return round(max(0, min(100, weighted))), breakdown
