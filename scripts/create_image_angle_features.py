"""Create posture and ankle/heel proxy features from squat image landmarks."""

from __future__ import annotations

import argparse
import csv
import logging
import sys
from collections import defaultdict
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
BACKEND_DIR = REPO_ROOT / "backend"
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from app.services.angle_calculation_service import (  # noqa: E402
    calculate_angle,
    calculate_hip_angle,
    calculate_knee_angle,
    calculate_trunk_angle,
)


LOGGER = logging.getLogger(__name__)
DEFAULT_INPUT_PATH = Path(
    "data/processed/pose_landmarks/zenodo_squat_dataset/zenodo_squat_landmarks.csv"
)
DEFAULT_OUTPUT_PATH = Path(
    "data/processed/angle_features/zenodo_squat_dataset/zenodo_squat_angle_features.csv"
)
REQUIRED_COLUMNS = {
    "source_dataset",
    "image_path",
    "label",
    "landmark_name",
    "x",
    "y",
}
OUTPUT_COLUMNS = [
    "source_dataset",
    "image_path",
    "label",
    "left_knee_angle",
    "right_knee_angle",
    "left_hip_angle",
    "right_hip_angle",
    "trunk_angle",
    "left_ankle_angle",
    "right_ankle_angle",
    "left_heel_foot_vertical_delta",
    "right_heel_foot_vertical_delta",
]


def average_point(left: dict[str, float], right: dict[str, float]) -> dict[str, float]:
    """Return the coordinate-wise midpoint of two landmarks."""
    return {
        "x": (left["x"] + right["x"]) / 2,
        "y": (left["y"] + right["y"]) / 2,
    }


def optional_angle(function, *points: dict[str, float] | None) -> float | None:
    """Calculate an angle only when all required landmarks are present."""
    if any(point is None for point in points):
        return None
    return function(*points)


def image_feature_row(
    source_dataset: str,
    image_path: str,
    label: str,
    points: dict[str, dict[str, float]],
) -> dict[str, object]:
    """Build one image-level feature row from named MediaPipe landmarks."""
    left_shoulder = points.get("left_shoulder")
    right_shoulder = points.get("right_shoulder")
    left_hip = points.get("left_hip")
    right_hip = points.get("right_hip")
    left_knee = points.get("left_knee")
    right_knee = points.get("right_knee")
    left_ankle = points.get("left_ankle")
    right_ankle = points.get("right_ankle")
    left_heel = points.get("left_heel")
    right_heel = points.get("right_heel")
    left_foot = points.get("left_foot_index")
    right_foot = points.get("right_foot_index")

    mid_shoulder = (
        average_point(left_shoulder, right_shoulder)
        if left_shoulder and right_shoulder
        else None
    )
    mid_hip = average_point(left_hip, right_hip) if left_hip and right_hip else None

    return {
        "source_dataset": source_dataset,
        "image_path": image_path,
        "label": label,
        "left_knee_angle": optional_angle(
            calculate_knee_angle, left_hip, left_knee, left_ankle
        ),
        "right_knee_angle": optional_angle(
            calculate_knee_angle, right_hip, right_knee, right_ankle
        ),
        "left_hip_angle": optional_angle(
            calculate_hip_angle, left_shoulder, left_hip, left_knee
        ),
        "right_hip_angle": optional_angle(
            calculate_hip_angle, right_shoulder, right_hip, right_knee
        ),
        "trunk_angle": optional_angle(calculate_trunk_angle, mid_shoulder, mid_hip),
        "left_ankle_angle": optional_angle(
            calculate_angle, left_knee, left_ankle, left_foot
        ),
        "right_ankle_angle": optional_angle(
            calculate_angle, right_knee, right_ankle, right_foot
        ),
        "left_heel_foot_vertical_delta": (
            round(abs(left_heel["y"] - left_foot["y"]), 6)
            if left_heel and left_foot
            else None
        ),
        "right_heel_foot_vertical_delta": (
            round(abs(right_heel["y"] - right_foot["y"]), 6)
            if right_heel and right_foot
            else None
        ),
    }


def create_angle_features(input_path: Path, output_path: Path) -> Path:
    """Aggregate long-format image landmarks into one feature row per image."""
    if not input_path.exists():
        raise FileNotFoundError(
            f"Image landmark CSV not found: {input_path}. Run extract_landmarks_from_images.py first."
        )

    groups: dict[
        tuple[str, str, str], dict[str, dict[str, float]]
    ] = defaultdict(dict)
    with input_path.open("r", newline="", encoding="utf-8") as csv_file:
        reader = csv.DictReader(csv_file)
        missing = REQUIRED_COLUMNS.difference(reader.fieldnames or [])
        if missing:
            raise ValueError(f"Landmark CSV is missing columns: {', '.join(sorted(missing))}")
        for row in reader:
            key = (row["source_dataset"], row["image_path"], row["label"])
            try:
                groups[key][row["landmark_name"].lower()] = {
                    "x": float(row["x"]),
                    "y": float(row["y"]),
                }
            except (TypeError, ValueError) as exc:
                raise ValueError(
                    f"Invalid x/y coordinate for {row.get('image_path', 'unknown image')}."
                ) from exc

    if not groups:
        raise ValueError("Image landmark CSV contains no landmark rows.")

    rows = [image_feature_row(*key, points) for key, points in sorted(groups.items())]
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", newline="", encoding="utf-8") as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=OUTPUT_COLUMNS)
        writer.writeheader()
        writer.writerows(rows)

    LOGGER.info("Saved %s image angle feature rows to %s", len(rows), output_path)
    return output_path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Create Zenodo squat image angle features.")
    parser.add_argument("--input", type=Path, default=DEFAULT_INPUT_PATH)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT_PATH)
    return parser.parse_args()


def main() -> int:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
    args = parse_args()
    try:
        output_path = create_angle_features(args.input, args.output)
    except Exception as exc:
        print(f"Image angle feature creation failed: {exc}", file=sys.stderr)
        return 1
    print(f"Saved Zenodo squat image angle features: {output_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
