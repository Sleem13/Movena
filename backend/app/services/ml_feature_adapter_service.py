"""Adapt detected pose frames to the Sprint 5 video-level feature contract."""

from __future__ import annotations

from statistics import mean, median, pstdev

import numpy as np
import pandas as pd

from app.services.angle_calculation_service import (
    calculate_hip_angle,
    calculate_knee_angle,
    calculate_trunk_angle,
)


ANGLE_COLUMNS = [
    "left_knee_angle",
    "right_knee_angle",
    "left_hip_angle",
    "right_hip_angle",
    "trunk_angle",
]


class MLFeatureCompatibilityError(ValueError):
    pass


def _midpoint(left: dict[str, float], right: dict[str, float]) -> dict[str, float]:
    return {"x": (left["x"] + right["x"]) / 2, "y": (left["y"] + right["y"]) / 2}


def _frame_angles(frame: dict) -> dict[str, float]:
    points = frame["landmarks"]
    required = {
        "left_shoulder", "right_shoulder", "left_hip", "right_hip",
        "left_knee", "right_knee", "left_ankle", "right_ankle",
    }
    if not required.issubset(points):
        raise MLFeatureCompatibilityError("Pose frames do not contain all required squat landmarks.")
    return {
        "left_knee_angle": calculate_knee_angle(points["left_hip"], points["left_knee"], points["left_ankle"]),
        "right_knee_angle": calculate_knee_angle(points["right_hip"], points["right_knee"], points["right_ankle"]),
        "left_hip_angle": calculate_hip_angle(points["left_shoulder"], points["left_hip"], points["left_knee"]),
        "right_hip_angle": calculate_hip_angle(points["right_shoulder"], points["right_hip"], points["right_knee"]),
        "trunk_angle": calculate_trunk_angle(
            _midpoint(points["left_shoulder"], points["right_shoulder"]),
            _midpoint(points["left_hip"], points["right_hip"]),
        ),
    }


def aggregate_pose_frames(frames: list[dict], expected_columns: list[str]) -> pd.DataFrame:
    if not frames:
        raise MLFeatureCompatibilityError("No pose frames are available for ML feature aggregation.")
    frame_data = pd.DataFrame([_frame_angles(frame) for frame in frames])
    feature_row: dict[str, float] = {}
    for angle in ANGLE_COLUMNS:
        values = frame_data[angle].dropna().astype(float).tolist()
        if not values:
            raise MLFeatureCompatibilityError(f"No usable values were available for {angle}.")
        feature_row.update({
            f"{angle}_mean": mean(values),
            f"{angle}_std": pstdev(values),
            f"{angle}_min": min(values),
            f"{angle}_max": max(values),
            f"{angle}_range": max(values) - min(values),
            f"{angle}_median": median(values),
            f"{angle}_q1": float(np.quantile(values, 0.25)),
            f"{angle}_q3": float(np.quantile(values, 0.75)),
        })
    feature_row["knee_angle_asymmetry"] = float(
        (frame_data["left_knee_angle"] - frame_data["right_knee_angle"]).abs().mean()
    )
    feature_row["hip_angle_asymmetry"] = float(
        (frame_data["left_hip_angle"] - frame_data["right_hip_angle"]).abs().mean()
    )
    feature_row["min_knee_angle"] = float(
        frame_data[["left_knee_angle", "right_knee_angle"]].min().min()
    )
    feature_row["max_trunk_angle"] = float(frame_data["trunk_angle"].max())
    feature_row["trunk_angle_range"] = float(
        frame_data["trunk_angle"].max() - frame_data["trunk_angle"].min()
    )
    feature_row["estimated_depth_proxy"] = 180.0 - feature_row["min_knee_angle"]

    missing = [column for column in expected_columns if column not in feature_row]
    if missing:
        raise MLFeatureCompatibilityError(
            "ML feature adapter cannot produce required columns: " + ", ".join(missing)
        )
    return pd.DataFrame([{column: feature_row.get(column, np.nan) for column in expected_columns}])
