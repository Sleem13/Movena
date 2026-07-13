"""Pose coverage and landmark-quality assessment for cautious interpretation."""

from __future__ import annotations

from statistics import mean, median
from typing import Any

from app.schemas.analysis_schema import PoseQuality


CRITICAL_LANDMARKS = (
    "left_shoulder", "right_shoulder", "left_hip", "right_hip",
    "left_knee", "right_knee", "left_ankle", "right_ankle",
    "left_heel", "right_heel", "left_foot_index", "right_foot_index",
)


def _level(score: float) -> str:
    return "high" if score >= 0.80 else "medium" if score >= 0.60 else "low"


def assess_pose_quality(frames: list[dict[str, Any]]) -> PoseQuality:
    if not frames:
        return PoseQuality(
            score=0, level="low", total_frames=0, pose_detected_frames=0,
            pose_detection_rate=0, average_visibility=0,
            critical_landmark_visibility=0, missing_critical_landmark_rate=1,
            low_confidence_frames=0, warnings=["No usable pose landmarks were available."],
        )

    total_frames = max(
        int(frame.get("source_total_frames", 0)) for frame in frames
    ) or (max(int(frame.get("frame_index", 0)) for frame in frames) + 1)
    detected = len(frames)
    detection_rate = min(1.0, detected / max(1, total_frames))
    visibility_values: list[float] = []
    critical_values: list[float] = []
    missing = 0
    low_confidence = 0
    body_widths: list[float] = []

    for frame in frames:
        landmarks = frame.get("landmarks", {})
        present_values = [
            float(point.get("visibility", 0))
            for point in landmarks.values()
            if isinstance(point, dict)
        ]
        visibility_values.extend(present_values)
        frame_critical: list[float] = []
        for name in CRITICAL_LANDMARKS:
            point = landmarks.get(name)
            if not point:
                missing += 1
                frame_critical.append(0.0)
            else:
                frame_critical.append(float(point.get("visibility", 0)))
        critical_values.extend(frame_critical)
        if frame.get("low_confidence") or (frame_critical and mean(frame_critical) < 0.45):
            low_confidence += 1
        for left, right in (("left_shoulder", "right_shoulder"), ("left_hip", "right_hip")):
            if left in landmarks and right in landmarks:
                body_widths.append(abs(float(landmarks[left]["x"]) - float(landmarks[right]["x"])))

    average_visibility = mean(visibility_values) if visibility_values else 0.0
    critical_visibility = mean(critical_values) if critical_values else 0.0
    missing_rate = missing / (detected * len(CRITICAL_LANDMARKS))
    low_rate = low_confidence / detected
    score = (
        (0.35 * detection_rate)
        + (0.25 * average_visibility)
        + (0.30 * critical_visibility)
        + (0.10 * (1 - low_rate))
    )

    typical_width = median(body_widths) if body_widths else 0.0
    camera_view = "front_or_oblique" if typical_width >= 0.08 else "side_or_oblique"
    camera_warning = None
    warnings: list[str] = []
    if camera_view == "side_or_oblique":
        camera_warning = "Side-view evidence is limited for evaluating possible knee valgus."
        warnings.append(camera_warning)
    if detection_rate < 0.80:
        warnings.append("Pose was not detected consistently across the recording.")
    if critical_visibility < 0.60:
        warnings.append("Some key joints or feet were not tracked clearly; review recording quality.")

    score = round(max(0.0, min(1.0, score)), 3)
    return PoseQuality(
        score=score,
        level=_level(score),
        total_frames=total_frames,
        pose_detected_frames=detected,
        pose_detection_rate=round(detection_rate, 3),
        average_visibility=round(average_visibility, 3),
        critical_landmark_visibility=round(critical_visibility, 3),
        missing_critical_landmark_rate=round(missing_rate, 3),
        low_confidence_frames=low_confidence,
        camera_view=camera_view,
        camera_view_warning=camera_warning,
        warnings=warnings,
    )
