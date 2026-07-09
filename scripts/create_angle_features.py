"""Create frame-level angle features from long-format landmark CSV files."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import pandas as pd

REPO_ROOT = Path(__file__).resolve().parents[1]
BACKEND_DIR = REPO_ROOT / "backend"
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from app.services.angle_calculation_service import calculate_angle, calculate_hip_angle, calculate_knee_angle, calculate_trunk_angle
from app.services.dataset_loader_service import load_and_normalize_dataset


DEFAULT_INPUT_DIR = Path("data/processed/pose_landmarks")
DEFAULT_OUTPUT_DIR = Path("data/processed/angle_features")


def point_lookup(frame: pd.DataFrame) -> dict[str, dict[str, float]]:
    lookup: dict[str, dict[str, float]] = {}
    for row in frame.to_dict("records"):
        lookup[str(row["landmark_name"]).lower()] = {
            "x": float(row["x"]),
            "y": float(row["y"]),
            "z": float(row.get("z", 0.0) or 0.0),
            "visibility": float(row.get("visibility", 0.0) or 0.0),
        }
    return lookup


def average_point(left: dict[str, float], right: dict[str, float]) -> dict[str, float]:
    return {
        "x": (left["x"] + right["x"]) / 2,
        "y": (left["y"] + right["y"]) / 2,
        "z": (left.get("z", 0.0) + right.get("z", 0.0)) / 2,
        "visibility": (left.get("visibility", 0.0) + right.get("visibility", 0.0)) / 2,
    }


def safe_angle(function, *points) -> float | None:
    try:
        return function(*points)
    except KeyError:
        return None


def create_features_for_file(input_path: Path, output_path: Path) -> Path:
    landmarks = load_and_normalize_dataset(input_path)
    feature_rows = []
    group_columns = ["source_dataset", "video_path", "exercise_name", "frame_index"]

    for group_values, frame in landmarks.groupby(group_columns, dropna=False):
        source_dataset, video_path, exercise_name, frame_index = group_values
        points = point_lookup(frame)
        left_shoulder = points.get("left_shoulder")
        right_shoulder = points.get("right_shoulder")
        left_hip = points.get("left_hip")
        right_hip = points.get("right_hip")
        left_knee = points.get("left_knee")
        right_knee = points.get("right_knee")
        left_ankle = points.get("left_ankle")
        right_ankle = points.get("right_ankle")
        left_foot = points.get("left_foot_index")
        right_foot = points.get("right_foot_index")

        mid_shoulder = (
            average_point(left_shoulder, right_shoulder)
            if left_shoulder and right_shoulder
            else None
        )
        mid_hip = average_point(left_hip, right_hip) if left_hip and right_hip else None

        feature_rows.append(
            {
                "source_dataset": source_dataset,
                "video_path": video_path,
                "exercise_name": exercise_name,
                "frame_index": int(frame_index),
                "timestamp": frame["timestamp"].dropna().iloc[0] if frame["timestamp"].notna().any() else None,
                "left_knee_angle": safe_angle(calculate_knee_angle, left_hip, left_knee, left_ankle)
                if left_hip and left_knee and left_ankle
                else None,
                "right_knee_angle": safe_angle(calculate_knee_angle, right_hip, right_knee, right_ankle)
                if right_hip and right_knee and right_ankle
                else None,
                "left_hip_angle": safe_angle(calculate_hip_angle, left_shoulder, left_hip, left_knee)
                if left_shoulder and left_hip and left_knee
                else None,
                "right_hip_angle": safe_angle(calculate_hip_angle, right_shoulder, right_hip, right_knee)
                if right_shoulder and right_hip and right_knee
                else None,
                "left_ankle_angle": safe_angle(calculate_angle, left_knee, left_ankle, left_foot)
                if left_knee and left_ankle and left_foot
                else None,
                "right_ankle_angle": safe_angle(calculate_angle, right_knee, right_ankle, right_foot)
                if right_knee and right_ankle and right_foot
                else None,
                "trunk_angle": safe_angle(calculate_trunk_angle, mid_shoulder, mid_hip)
                if mid_shoulder and mid_hip
                else None,
                "correctness_label": frame["correctness_label"].iloc[0],
                "detected_issue": frame["detected_issue"].iloc[0],
                "quality_score": frame["quality_score"].iloc[0],
            }
        )

    features = pd.DataFrame(feature_rows)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    features.to_csv(output_path, index=False)
    return output_path


def iter_landmark_files(input_dir: Path) -> list[Path]:
    return sorted(
        path
        for path in input_dir.glob("*.csv")
        if path.name != "failed_videos.csv" and "landmarks" in path.stem
    )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Create angle features from landmark CSV files.")
    parser.add_argument("--input", type=Path, default=None)
    parser.add_argument("--input-dir", type=Path, default=DEFAULT_INPUT_DIR)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    input_files = [args.input] if args.input else iter_landmark_files(args.input_dir)
    if not input_files:
        print(f"No landmark CSV files found in {args.input_dir}.", file=sys.stderr)
        return 1

    for input_path in input_files:
        output_path = args.output_dir / f"{input_path.stem.replace('_landmarks', '')}_angles.csv"
        try:
            created = create_features_for_file(input_path, output_path)
            print(f"Saved angle features: {created}")
        except Exception as exc:
            print(f"Failed to create features for {input_path}: {exc}", file=sys.stderr)
            return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
