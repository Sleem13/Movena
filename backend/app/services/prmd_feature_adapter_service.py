"""Convert Movena pose frames to the external UI-PRMD model contract."""

from __future__ import annotations

from collections.abc import Sequence

import numpy as np


PRMD_JOINT_COUNT = 22
PRMD_FEATURE_COUNT = PRMD_JOINT_COUNT * 3
MIN_SCALE = 1e-4

REQUIRED_LANDMARKS = (
    "nose",
    "left_shoulder",
    "right_shoulder",
    "left_elbow",
    "right_elbow",
    "left_wrist",
    "right_wrist",
    "left_hip",
    "right_hip",
    "left_knee",
    "right_knee",
    "left_ankle",
    "right_ankle",
    "left_foot_index",
    "right_foot_index",
)

SUPPORTED_NORMALIZERS = (
    "pelvis_width",
    "shoulder_width",
    "spine_length",
)


class PRMDFeatureCompatibilityError(ValueError):
    """Raised when pose data cannot safely satisfy the external model contract."""


def _point(points: dict[str, object], name: str, *, mirror_x: bool) -> np.ndarray:
    point = points.get(name)
    if not isinstance(point, dict):
        raise PRMDFeatureCompatibilityError(f"Pose frame is missing required landmark: {name}.")
    try:
        x = float(point["x"])
        y = float(point["y"])
        z = float(point["z"])
    except (KeyError, TypeError, ValueError) as exc:
        raise PRMDFeatureCompatibilityError(f"Pose landmark {name} has invalid coordinates.") from exc
    coordinates = np.asarray([-x if mirror_x else x, -y, z], dtype=np.float32)
    if not np.isfinite(coordinates).all():
        raise PRMDFeatureCompatibilityError(f"Pose landmark {name} has non-finite coordinates.")
    return coordinates


def extract_prmd_frame_features(
    frame: dict[str, object],
    *,
    mirror_x: bool = False,
    min_visibility: float = 0.3,
) -> np.ndarray:
    """Map one named MediaPipe frame to the source model's ordered 66 features."""

    if frame.get("subject_continuity_warning"):
        raise PRMDFeatureCompatibilityError(
            "PRMD adaptation is disabled when subject continuity is uncertain."
        )
    if frame.get("low_confidence") is True:
        raise PRMDFeatureCompatibilityError("PRMD adaptation requires a high-confidence pose frame.")
    points = frame.get("landmarks")
    if not isinstance(points, dict):
        raise PRMDFeatureCompatibilityError("Pose frame does not contain a landmarks mapping.")

    for name in REQUIRED_LANDMARKS:
        point = points.get(name)
        if not isinstance(point, dict):
            raise PRMDFeatureCompatibilityError(f"Pose frame is missing required landmark: {name}.")
        try:
            visibility = float(point.get("visibility", 0.0))
        except (TypeError, ValueError) as exc:
            raise PRMDFeatureCompatibilityError(f"Pose landmark {name} has invalid visibility.") from exc
        if not np.isfinite(visibility) or visibility < min_visibility:
            raise PRMDFeatureCompatibilityError(
                f"Pose landmark {name} is below the required visibility threshold."
            )

    def point(name: str) -> np.ndarray:
        return _point(points, name, mirror_x=mirror_x)

    def midpoint(left: str, right: str) -> np.ndarray:
        return (point(left) + point(right)) / 2.0

    shoulder_midpoint = midpoint("left_shoulder", "right_shoulder")
    prmd = np.asarray(
        [
            midpoint("left_hip", "right_hip"),
            point("left_hip"),
            shoulder_midpoint,
            shoulder_midpoint,
            point("nose"),
            point("nose"),
            point("left_shoulder"),
            point("left_elbow"),
            point("left_wrist"),
            point("left_wrist"),
            point("right_shoulder"),
            point("right_elbow"),
            point("right_wrist"),
            point("right_wrist"),
            point("right_hip"),
            point("right_knee"),
            point("right_ankle"),
            point("right_foot_index"),
            point("left_hip"),
            point("left_knee"),
            point("left_ankle"),
            point("left_foot_index"),
        ],
        dtype=np.float32,
    )
    return prmd.reshape(PRMD_FEATURE_COUNT)


def extract_prmd_sequence_features(
    frames: Sequence[dict[str, object]],
    *,
    mirror_x: bool = False,
    min_visibility: float = 0.3,
) -> np.ndarray:
    if not frames:
        raise PRMDFeatureCompatibilityError("No pose frames are available for PRMD adaptation.")
    return np.stack(
        [
            extract_prmd_frame_features(
                frame,
                mirror_x=mirror_x,
                min_visibility=min_visibility,
            )
            for frame in frames
        ]
    ).astype(np.float32, copy=False)


def _resize_sequence(sequence: np.ndarray, target_frames: int) -> np.ndarray:
    if target_frames <= 0:
        raise PRMDFeatureCompatibilityError("target_frames must be greater than zero.")
    if sequence.shape[0] == target_frames:
        return sequence.copy()
    try:
        import cv2
    except ImportError as exc:
        raise PRMDFeatureCompatibilityError(
            "OpenCV is required to match the external model's sequence interpolation."
        ) from exc
    return cv2.resize(
        sequence,
        (PRMD_FEATURE_COUNT, target_frames),
        interpolation=cv2.INTER_LINEAR,
    ).astype(np.float32, copy=False)


def normalize_prmd_sequence(
    sequence: Sequence[Sequence[float]] | np.ndarray,
    *,
    target_frames: int,
    normalizer: str,
) -> np.ndarray:
    """Resize, root-center, and scale a sequence to ``(1, T, 66)``."""

    data = np.asarray(sequence, dtype=np.float32)
    if data.ndim != 2 or data.shape[1] != PRMD_FEATURE_COUNT or data.shape[0] == 0:
        raise PRMDFeatureCompatibilityError("Expected a non-empty PRMD sequence shaped (frames, 66).")
    if not np.isfinite(data).all():
        raise PRMDFeatureCompatibilityError("PRMD sequence contains non-finite values.")
    if normalizer not in SUPPORTED_NORMALIZERS:
        raise PRMDFeatureCompatibilityError(f"Unsupported PRMD normalizer: {normalizer}.")

    joints = _resize_sequence(data, target_frames).reshape(target_frames, PRMD_JOINT_COUNT, 3)
    joints = joints - joints[:, 0:1, :]
    if normalizer == "pelvis_width":
        scale = np.linalg.norm(joints[:, 18, :] - joints[:, 14, :], axis=1)
    elif normalizer == "shoulder_width":
        scale = np.linalg.norm(joints[:, 6, :] - joints[:, 10, :], axis=1)
    else:
        scale = np.linalg.norm(joints[:, 2, :], axis=1)

    if not np.isfinite(scale).all() or np.any(scale <= MIN_SCALE):
        raise PRMDFeatureCompatibilityError(
            f"PRMD {normalizer} scale is degenerate in one or more frames."
        )
    normalized = joints / scale[:, np.newaxis, np.newaxis]
    return normalized.reshape(1, target_frames, PRMD_FEATURE_COUNT).astype(np.float32, copy=False)


def prepare_prmd_model_input(
    frames: Sequence[dict[str, object]],
    *,
    target_frames: int,
    normalizer: str,
    mirror_x: bool = False,
    min_visibility: float = 0.3,
) -> np.ndarray:
    sequence = extract_prmd_sequence_features(
        frames,
        mirror_x=mirror_x,
        min_visibility=min_visibility,
    )
    return normalize_prmd_sequence(
        sequence,
        target_frames=target_frames,
        normalizer=normalizer,
    )


__all__ = [
    "PRMD_FEATURE_COUNT",
    "PRMD_JOINT_COUNT",
    "PRMDFeatureCompatibilityError",
    "SUPPORTED_NORMALIZERS",
    "extract_prmd_frame_features",
    "extract_prmd_sequence_features",
    "normalize_prmd_sequence",
    "prepare_prmd_model_input",
]
