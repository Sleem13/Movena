"""Aggregate frame-level custom squat angles into video-level ML features."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd


ANGLE_COLUMNS = [
    "left_knee_angle",
    "right_knee_angle",
    "left_hip_angle",
    "right_hip_angle",
    "trunk_angle",
]
STATISTICS = ["mean", "std", "min", "max", "range", "median", "q1", "q3"]
METADATA_COLUMNS = ["video_path", "label", "split", "source_dataset"]
DEFAULT_ANGLES = Path("data/processed/angle_features/custom_squat_videos_angle_features.csv")
DEFAULT_LABELS = Path("data/processed/labels/custom_squat_videos_labels.csv")
DEFAULT_SPLIT = Path("data/processed/labels/custom_squat_curated_split.csv")
DEFAULT_OUTPUT = Path("data/processed/features/squat_video_training_features.csv")


def normalize_video_path(value: object) -> str:
    return str(value).strip().replace("\\", "/")


def feature_columns() -> list[str]:
    columns = [f"{angle}_{stat}" for angle in ANGLE_COLUMNS for stat in STATISTICS]
    return columns + [
        "knee_angle_asymmetry",
        "hip_angle_asymmetry",
        "min_knee_angle",
        "max_trunk_angle",
        "trunk_angle_range",
        "estimated_depth_proxy",
    ]


def _validate_columns(frame: pd.DataFrame, required: set[str], source: Path) -> None:
    missing = required.difference(frame.columns)
    if missing:
        raise ValueError(f"{source} is missing columns: {', '.join(sorted(missing))}")


def prepare_training_dataset(
    angles_path: Path,
    labels_path: Path,
    split_path: Path | None,
    output_path: Path,
) -> pd.DataFrame:
    if not angles_path.exists():
        raise FileNotFoundError(f"Angle feature CSV not found: {angles_path}")
    if not labels_path.exists():
        raise FileNotFoundError(f"Video label CSV not found: {labels_path}")

    angles = pd.read_csv(angles_path)
    labels = pd.read_csv(labels_path)
    _validate_columns(angles, {"video_path", "source_dataset", *ANGLE_COLUMNS}, angles_path)
    _validate_columns(labels, {"video_path", "label", "is_supported_video"}, labels_path)
    angles["video_key"] = angles["video_path"].map(normalize_video_path)
    labels["video_key"] = labels["video_path"].map(normalize_video_path)
    labels = labels[labels["is_supported_video"].astype(str).str.lower() == "true"]
    labels = labels[["video_key", "label"]].drop_duplicates("video_key")

    if split_path and split_path.exists():
        split = pd.read_csv(split_path)
        _validate_columns(split, {"video_path", "label", "split"}, split_path)
        split["video_key"] = split["video_path"].map(normalize_video_path)
        split = split[["video_key", "label", "split"]].drop_duplicates("video_key")
        labels = labels.drop(columns="label").merge(split, on="video_key", how="left")
    else:
        labels["split"] = "development"

    merged = angles.merge(labels, on="video_key", how="inner", suffixes=("", "_curated"))
    if "label_curated" in merged:
        merged["label"] = merged["label_curated"].fillna(merged.get("label", "unlabeled"))
    merged["split"] = merged["split"].fillna("development")
    merged = merged[merged["label"].notna() & (merged["label"] != "unlabeled")].copy()
    for column in ANGLE_COLUMNS:
        merged[column] = pd.to_numeric(merged[column], errors="coerce")
    if merged.empty:
        raise ValueError("No labeled custom squat angle rows matched the metadata.")

    records: list[dict[str, object]] = []
    for video_key, group in merged.groupby("video_key", sort=True):
        record: dict[str, object] = {
            "video_path": video_key,
            "label": str(group["label"].iloc[0]),
            "split": str(group["split"].iloc[0]),
            "source_dataset": str(group["source_dataset"].iloc[0]),
        }
        for angle in ANGLE_COLUMNS:
            values = group[angle].dropna()
            record.update(
                {
                    f"{angle}_mean": values.mean(),
                    f"{angle}_std": values.std(ddof=0),
                    f"{angle}_min": values.min(),
                    f"{angle}_max": values.max(),
                    f"{angle}_range": values.max() - values.min(),
                    f"{angle}_median": values.median(),
                    f"{angle}_q1": values.quantile(0.25),
                    f"{angle}_q3": values.quantile(0.75),
                }
            )
        record["knee_angle_asymmetry"] = (
            group["left_knee_angle"] - group["right_knee_angle"]
        ).abs().mean()
        record["hip_angle_asymmetry"] = (
            group["left_hip_angle"] - group["right_hip_angle"]
        ).abs().mean()
        record["min_knee_angle"] = group[["left_knee_angle", "right_knee_angle"]].min().min()
        record["max_trunk_angle"] = group["trunk_angle"].max()
        record["trunk_angle_range"] = group["trunk_angle"].max() - group["trunk_angle"].min()
        record["estimated_depth_proxy"] = 180.0 - float(record["min_knee_angle"])
        records.append(record)

    result = pd.DataFrame(records)[METADATA_COLUMNS + feature_columns()]
    result.replace([np.inf, -np.inf], np.nan, inplace=True)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    result.to_csv(output_path, index=False)
    return result


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--angles", type=Path, default=DEFAULT_ANGLES)
    parser.add_argument("--labels", type=Path, default=DEFAULT_LABELS)
    parser.add_argument("--split", type=Path, default=DEFAULT_SPLIT)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        data = prepare_training_dataset(args.angles, args.labels, args.split, args.output)
    except Exception as exc:
        print(f"Training dataset preparation failed: {exc}", file=sys.stderr)
        return 1
    print(f"Saved {len(data)} video-level rows to {args.output}")
    print("Class distribution: " + json.dumps(data["label"].value_counts().to_dict(), sort_keys=True))
    print("Split distribution: " + json.dumps(data["split"].value_counts().to_dict(), sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
