"""Validate augmented squat videos and their source/augmentation registry."""

from __future__ import annotations

import argparse
import csv
import json
import sys
from collections import Counter
from pathlib import Path

from augment_custom_squat_videos import LABELS, METADATA_COLUMNS, video_metadata


DEFAULT_INPUT = Path("data/augmented/custom_videos")
DEFAULT_METADATA = Path("data/processed/labels/augmented_custom_squat_videos_labels.csv")


def validate_augmented_metadata(input_dir: Path, metadata_path: Path) -> tuple[list[dict[str, str]], list[str]]:
    if not metadata_path.exists():
        metadata_path.parent.mkdir(parents=True, exist_ok=True)
        with metadata_path.open("w", newline="", encoding="utf-8") as handle:
            csv.DictWriter(handle, fieldnames=METADATA_COLUMNS).writeheader()
        return [], ["No augmentation registry existed; created an empty metadata CSV."]
    with metadata_path.open("r", newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        missing = set(METADATA_COLUMNS).difference(reader.fieldnames or [])
        if missing:
            raise ValueError("Augmentation metadata is missing columns: " + ", ".join(sorted(missing)))
        rows = list(reader)
    warnings: list[str] = []
    for row in rows:
        source = Path(row["source_video_path"])
        augmented = Path(row["augmented_video_path"])
        if not source.exists():
            warnings.append(f"Missing source: {source}")
            row["safe_for_training"] = "false"
        if not augmented.exists() or not augmented.is_relative_to(input_dir):
            warnings.append(f"Missing or out-of-scope augmented file: {augmented}")
            row["safe_for_training"] = "false"
        if row["original_label"] != row["augmented_label"]:
            warnings.append(f"Label-changing augmentation requires manual review: {augmented}")
            row["safe_for_training"] = "false"
        try:
            json.loads(row["augmentation_parameters"] or "{}")
        except json.JSONDecodeError:
            warnings.append(f"Invalid augmentation parameters JSON: {augmented}")
            row["safe_for_training"] = "false"
    with metadata_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=METADATA_COLUMNS)
        writer.writeheader()
        writer.writerows(rows)
    return rows, warnings


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input-dir", type=Path, default=DEFAULT_INPUT)
    parser.add_argument("--metadata", type=Path, default=DEFAULT_METADATA)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        rows, warnings = validate_augmented_metadata(args.input_dir, args.metadata)
    except Exception as exc:
        print(f"Augmented video validation failed: {exc}", file=sys.stderr)
        return 1
    counts = Counter(row["augmented_label"] for row in rows)
    print(f"Validated {len(rows)} augmented video records.")
    for label in LABELS:
        print(f"{label}: {counts[label]}")
    for warning in warnings:
        print(f"WARNING: {warning}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
