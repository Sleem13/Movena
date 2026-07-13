"""Build Sprint 7 video-level features with real/augmented source lineage."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import numpy as np
import pandas as pd

from prepare_squat_training_dataset import ANGLE_COLUMNS, feature_columns, normalize_video_path


DEFAULT_REAL_ANGLES = Path("data/processed/angle_features/custom_squat_videos_angle_features.csv")
DEFAULT_REAL_LABELS = Path("data/processed/labels/custom_squat_videos_labels.csv")
DEFAULT_SPLIT = Path("data/processed/labels/custom_squat_curated_split.csv")
DEFAULT_AUGMENTED_ANGLES = Path("data/processed/angle_features/augmented_custom_squat_angle_features.csv")
DEFAULT_AUGMENTED_LABELS = Path("data/processed/labels/augmented_custom_squat_videos_labels.csv")
DEFAULT_MANUAL_REPS = Path("data/processed/labels/custom_squat_manual_rep_counts.csv")
DEFAULT_OUTPUT = Path("data/processed/features/squat_video_training_features_v2.csv")
META_COLUMNS = [
    "video_path", "label", "split", "source_dataset", "source_type",
    "original_label", "augmented_label", "manual_expected_reps",
    "manual_rep_count_validated",
]


def _aggregate(group: pd.DataFrame) -> dict[str, float]:
    record: dict[str, float] = {}
    for angle in ANGLE_COLUMNS:
        values = pd.to_numeric(group[angle], errors="coerce").dropna()
        record.update({
            f"{angle}_mean": values.mean(),
            f"{angle}_std": values.std(ddof=0),
            f"{angle}_min": values.min(),
            f"{angle}_max": values.max(),
            f"{angle}_range": values.max() - values.min(),
            f"{angle}_median": values.median(),
            f"{angle}_q1": values.quantile(0.25),
            f"{angle}_q3": values.quantile(0.75),
        })
    record["knee_angle_asymmetry"] = (
        group["left_knee_angle"] - group["right_knee_angle"]
    ).abs().mean()
    record["hip_angle_asymmetry"] = (
        group["left_hip_angle"] - group["right_hip_angle"]
    ).abs().mean()
    record["min_knee_angle"] = group[["left_knee_angle", "right_knee_angle"]].min().min()
    record["max_trunk_angle"] = group["trunk_angle"].max()
    record["trunk_angle_range"] = group["trunk_angle"].max() - group["trunk_angle"].min()
    record["estimated_depth_proxy"] = 180.0 - record["min_knee_angle"]
    return record


def _aggregate_rows(rows: pd.DataFrame, metadata: pd.DataFrame) -> pd.DataFrame:
    rows = rows.copy()
    rows.drop(
        columns=[
            column for column in [
                "label", "split", "source_type", "original_label", "augmented_label"
            ] if column in rows.columns
        ],
        inplace=True,
    )
    rows["video_key"] = rows["video_path"].map(normalize_video_path)
    merged = rows.merge(metadata, on="video_key", how="inner")
    output = []
    for video_key, group in merged.groupby("video_key", sort=True):
        first = group.iloc[0]
        output.append({
            "video_path": video_key,
            "label": first["label"],
            "split": first["split"],
            "source_dataset": first["source_dataset_meta"],
            "source_type": first["source_type"],
            "original_label": first["original_label"],
            "augmented_label": first["augmented_label"],
            "manual_expected_reps": first["manual_expected_reps"],
            "manual_rep_count_validated": bool(first["manual_rep_count_validated"]),
            **_aggregate(group),
        })
    return pd.DataFrame(output)


def prepare_training_dataset_v2(
    real_angles_path: Path,
    real_labels_path: Path,
    split_path: Path,
    output_path: Path,
    include_augmented: bool = False,
    augmented_angles_path: Path = DEFAULT_AUGMENTED_ANGLES,
    augmented_labels_path: Path = DEFAULT_AUGMENTED_LABELS,
    manual_reps_path: Path = DEFAULT_MANUAL_REPS,
) -> pd.DataFrame:
    real_angles = pd.read_csv(real_angles_path)
    real_labels = pd.read_csv(real_labels_path)
    required_angles = {"video_path", *ANGLE_COLUMNS}
    if missing := required_angles.difference(real_angles.columns):
        raise ValueError("Real angle CSV is missing: " + ", ".join(sorted(missing)))
    real_labels = real_labels[
        (real_labels["is_supported_video"].astype(str).str.lower() == "true")
        & (real_labels["label"] != "unlabeled")
    ].copy()
    real_labels["video_key"] = real_labels["video_path"].map(normalize_video_path)
    splits = pd.read_csv(split_path) if split_path.exists() else pd.DataFrame(columns=["video_path", "split"])
    splits["video_key"] = splits.get("video_path", pd.Series(dtype=str)).map(normalize_video_path)
    real_meta = real_labels[["video_key", "label", "source_dataset"]].merge(
        splits[["video_key", "split"]], on="video_key", how="left"
    )
    real_meta["split"] = real_meta["split"].fillna("development_unassigned")
    real_meta["source_dataset_meta"] = real_meta["source_dataset"]
    real_meta["source_type"] = "real"
    real_meta["original_label"] = real_meta["label"]
    real_meta["augmented_label"] = ""
    manual = pd.DataFrame(columns=["video_key", "manual_expected_reps"])
    if manual_reps_path.exists():
        manual = pd.read_csv(manual_reps_path)
        required_manual = {"video_path", "expected_reps"}
        if missing := required_manual.difference(manual.columns):
            raise ValueError("Manual rep-count CSV is missing: " + ", ".join(sorted(missing)))
        manual["video_key"] = manual["video_path"].map(normalize_video_path)
        manual["manual_expected_reps"] = pd.to_numeric(manual["expected_reps"], errors="coerce")
        manual = manual[["video_key", "manual_expected_reps"]].drop_duplicates("video_key")
    real_meta = real_meta.merge(manual, on="video_key", how="left")
    real_meta["manual_rep_count_validated"] = real_meta["manual_expected_reps"].notna()
    frames = [_aggregate_rows(real_angles, real_meta)]

    if include_augmented:
        if not augmented_angles_path.exists():
            print(
                f"WARNING: augmented angles not found at {augmented_angles_path}; continuing with real videos only.",
                file=sys.stderr,
            )
        elif not augmented_labels_path.exists():
            print("WARNING: augmented label registry is missing; continuing with real videos only.", file=sys.stderr)
        else:
            augmented_angles = pd.read_csv(augmented_angles_path)
            augmented_labels = pd.read_csv(augmented_labels_path)
            safe = augmented_labels["safe_for_training"].astype(str).str.lower() == "true"
            augmented_labels = augmented_labels[safe].copy()
            augmented_labels["video_key"] = augmented_labels["augmented_video_path"].map(normalize_video_path)
            augmented_labels["source_key"] = augmented_labels["source_video_path"].map(normalize_video_path)
            source_splits = splits[["video_key", "split"]].rename(columns={"video_key": "source_key"})
            aug_meta = augmented_labels.merge(source_splits, on="source_key", how="left")
            aug_meta["split"] = aug_meta["split"].fillna("development_unassigned")
            aug_meta["label"] = aug_meta["augmented_label"]
            aug_meta["source_dataset_meta"] = "augmented_custom_squat_videos"
            aug_meta["source_type"] = "augmented"
            source_manual = manual.rename(columns={"video_key": "source_key"})
            aug_meta = aug_meta.merge(source_manual, on="source_key", how="left")
            aug_meta["manual_rep_count_validated"] = aug_meta["manual_expected_reps"].notna()
            frames.append(_aggregate_rows(augmented_angles, aug_meta))

    result = pd.concat(frames, ignore_index=True)
    result.replace([np.inf, -np.inf], np.nan, inplace=True)
    result = result[META_COLUMNS + feature_columns()]
    output_path.parent.mkdir(parents=True, exist_ok=True)
    result.to_csv(output_path, index=False)
    return result


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--real-angles", type=Path, default=DEFAULT_REAL_ANGLES)
    parser.add_argument("--real-labels", type=Path, default=DEFAULT_REAL_LABELS)
    parser.add_argument("--split", type=Path, default=DEFAULT_SPLIT)
    parser.add_argument("--augmented-angles", type=Path, default=DEFAULT_AUGMENTED_ANGLES)
    parser.add_argument("--augmented-labels", type=Path, default=DEFAULT_AUGMENTED_LABELS)
    parser.add_argument("--manual-reps", type=Path, default=DEFAULT_MANUAL_REPS)
    parser.add_argument("--include-augmented", action="store_true")
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        data = prepare_training_dataset_v2(
            args.real_angles, args.real_labels, args.split, args.output,
            args.include_augmented, args.augmented_angles, args.augmented_labels,
            args.manual_reps,
        )
    except Exception as exc:
        print(f"Training dataset v2 preparation failed: {exc}", file=sys.stderr)
        return 1
    print(f"Saved {len(data)} v2 video rows to {args.output}")
    print(data.groupby(["source_type", "label"]).size().to_string())
    real = data[data["source_type"] == "real"]
    validated = int(real["manual_rep_count_validated"].astype(bool).sum())
    print(f"Manual rep counts validated: {validated}/{len(real)} real videos")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
