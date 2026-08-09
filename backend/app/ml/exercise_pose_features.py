"""Shared 17-keypoint pose feature contract for exercise recognition."""

from __future__ import annotations

from collections.abc import Sequence

import numpy as np


KEYPOINT_COUNT = 17
CONFIDENCE_THRESHOLD = 0.3
MIN_VISIBLE_KEYPOINTS = 10
CRITICAL_KEYPOINTS = (5, 6, 11, 12)
ANGLE_DEFINITIONS = {
    "angle_left_knee": (11, 13, 15),
    "angle_right_knee": (12, 14, 16),
    "angle_left_hip": (5, 11, 13),
    "angle_right_hip": (6, 12, 14),
    "angle_left_elbow": (5, 7, 9),
    "angle_right_elbow": (6, 8, 10),
}
COCO_LANDMARK_NAMES = (
    "nose", "left_eye", "right_eye", "left_ear", "right_ear",
    "left_shoulder", "right_shoulder", "left_elbow", "right_elbow",
    "left_wrist", "right_wrist", "left_hip", "right_hip", "left_knee",
    "right_knee", "left_ankle", "right_ankle",
)


def feature_columns() -> list[str]:
    coordinates = [axis for index in range(KEYPOINT_COUNT) for axis in (f"joint_{index}_x", f"joint_{index}_y")]
    return coordinates + list(ANGLE_DEFINITIONS)


def _angle(a: np.ndarray, b: np.ndarray, c: np.ndarray) -> float:
    first = a - b
    second = c - b
    dot = float(np.dot(first, second))
    cross = float(first[0] * second[1] - first[1] * second[0])
    return float(np.degrees(abs(np.arctan2(cross, dot))))


def extract_pose_features(
    keypoints_xy: Sequence[Sequence[float]] | np.ndarray,
    confidence: Sequence[float] | np.ndarray,
) -> dict[str, float] | None:
    """Return the ordered 40-feature contract, or ``None`` for an unusable pose."""

    xy = np.asarray(keypoints_xy, dtype=np.float64)
    conf = np.asarray(confidence, dtype=np.float64)
    if xy.shape != (KEYPOINT_COUNT, 2) or conf.shape != (KEYPOINT_COUNT,):
        raise ValueError("Expected 17 two-dimensional keypoints and 17 confidence values.")
    if int(np.count_nonzero(conf >= CONFIDENCE_THRESHOLD)) < MIN_VISIBLE_KEYPOINTS:
        return None
    if any(conf[index] < CONFIDENCE_THRESHOLD for index in CRITICAL_KEYPOINTS):
        return None

    mid_hip = (xy[11] + xy[12]) / 2.0
    mid_shoulder = (xy[5] + xy[6]) / 2.0
    torso_height = float(np.linalg.norm(mid_shoulder - mid_hip))
    if not np.isfinite(torso_height) or torso_height <= 1e-8:
        return None
    normalized = (xy - mid_hip) / torso_height

    values: dict[str, float] = {}
    for index in range(KEYPOINT_COUNT):
        values[f"joint_{index}_x"] = float(normalized[index, 0])
        values[f"joint_{index}_y"] = float(normalized[index, 1])
    for name, (first, vertex, third) in ANGLE_DEFINITIONS.items():
        values[name] = _angle(normalized[first], normalized[vertex], normalized[third])
    return values


def extract_mediapipe_frame_features(frame: dict[str, object]) -> dict[str, float] | None:
    """Convert one runtime MediaPipe frame into the trained COCO-17 feature contract."""

    points = frame.get("landmarks", {})
    if not isinstance(points, dict):
        return None
    xy = np.zeros((KEYPOINT_COUNT, 2), dtype=np.float64)
    confidence = np.zeros(KEYPOINT_COUNT, dtype=np.float64)
    for index, name in enumerate(COCO_LANDMARK_NAMES):
        point = points.get(name, {})
        if not isinstance(point, dict):
            continue
        try:
            xy[index] = [float(point.get("x", 0.0)), float(point.get("y", 0.0))]
            confidence[index] = float(point.get("visibility", 0.0))
        except (TypeError, ValueError):
            return None
    return extract_pose_features(xy, confidence)


def extract_mediapipe_sequence_features(
    frames: Sequence[dict[str, object]],
) -> list[dict[str, float]]:
    """Return usable ordered pose features for runtime video recognition."""

    return [features for frame in frames if (features := extract_mediapipe_frame_features(frame))]
