"""Create or extend the Sprint 8A manual squat annotation registry."""

from __future__ import annotations

import argparse
import csv
import sys
from pathlib import Path

import pandas as pd


DEFAULT_CUSTOM_LABELS = Path("data/processed/labels/custom_squat_videos_labels.csv")
DEFAULT_AUGMENTED_LABELS = Path("data/processed/labels/augmented_custom_squat_videos_labels.csv")
DEFAULT_OUTPUT = Path("data/processed/labels/manual_rep_annotations.csv")
ANNOTATION_COLUMNS = [
    "video_path",
    "participant_id",
    "session_id",
    "exercise_label",
    "expected_reps",
    "view_type",
    "recording_quality",
    "annotator",
    "annotation_confidence",
    "notes",
]


def normalize_path(value: object) -> str:
    return str(value).strip().replace("\\", "/")


def _load_candidates(custom_labels_path: Path, augmented_labels_path: Path) -> list[dict[str, str]]:
    if not custom_labels_path.exists():
        raise FileNotFoundError(f"Custom squat label registry not found: {custom_labels_path}")
    custom = pd.read_csv(custom_labels_path)
    required = {"video_path", "label", "is_supported_video"}
    if missing := required.difference(custom.columns):
        raise ValueError("Custom label registry is missing: " + ", ".join(sorted(missing)))
    supported = custom[custom["is_supported_video"].astype(str).str.lower() == "true"]
    candidates = [
        {"video_path": normalize_path(row.video_path), "exercise_label": str(row.label)}
        for row in supported.itertuples()
    ]

    if augmented_labels_path.exists():
        augmented = pd.read_csv(augmented_labels_path)
        required_augmented = {"augmented_video_path", "augmented_label", "safe_for_training"}
        if missing := required_augmented.difference(augmented.columns):
            raise ValueError("Augmented label registry is missing: " + ", ".join(sorted(missing)))
        safe = augmented[augmented["safe_for_training"].astype(str).str.lower() == "true"]
        candidates.extend(
            {
                "video_path": normalize_path(row.augmented_video_path),
                "exercise_label": str(row.augmented_label),
            }
            for row in safe.itertuples()
        )
    return list({row["video_path"]: row for row in candidates}.values())


def create_annotation_template(
    custom_labels_path: Path,
    augmented_labels_path: Path,
    output_path: Path,
) -> tuple[pd.DataFrame, int, int]:
    candidates = _load_candidates(custom_labels_path, augmented_labels_path)
    existing: dict[str, dict[str, str]] = {}
    if output_path.exists():
        with output_path.open("r", newline="", encoding="utf-8-sig") as handle:
            reader = csv.DictReader(handle)
            if missing := set(ANNOTATION_COLUMNS).difference(reader.fieldnames or []):
                raise ValueError("Existing annotation file is missing: " + ", ".join(sorted(missing)))
            for row in reader:
                key = normalize_path(row.get("video_path", ""))
                if key and key not in existing:
                    existing[key] = {column: row.get(column, "") for column in ANNOTATION_COLUMNS}

    rows: list[dict[str, str]] = []
    added = 0
    preserved = 0
    candidate_paths = set()
    for candidate in sorted(candidates, key=lambda row: row["video_path"]):
        key = candidate["video_path"]
        candidate_paths.add(key)
        if key in existing:
            row = existing[key]
            row["video_path"] = key
            row["exercise_label"] = row["exercise_label"] or candidate["exercise_label"]
            preserved += 1
        else:
            row = {column: "" for column in ANNOTATION_COLUMNS}
            row.update(candidate)
            added += 1
        rows.append(row)

    # Preserve reviewed historical rows even if source metadata is temporarily unavailable.
    for key, row in sorted(existing.items()):
        if key not in candidate_paths:
            row["video_path"] = key
            rows.append(row)
            preserved += 1

    output_path.parent.mkdir(parents=True, exist_ok=True)
    result = pd.DataFrame(rows, columns=ANNOTATION_COLUMNS)
    result.to_csv(output_path, index=False)
    return result, added, preserved


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--custom-labels", type=Path, default=DEFAULT_CUSTOM_LABELS)
    parser.add_argument("--augmented-labels", type=Path, default=DEFAULT_AUGMENTED_LABELS)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        data, added, preserved = create_annotation_template(
            args.custom_labels, args.augmented_labels, args.output
        )
    except Exception as exc:
        print(f"Manual annotation template creation failed: {exc}", file=sys.stderr)
        return 1
    print(f"Saved {len(data)} annotation rows to {args.output}")
    print(f"Added rows: {added}; preserved rows: {preserved}")
    print("Human review is required; participant IDs and expected reps are never inferred.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
