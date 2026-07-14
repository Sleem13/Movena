"""Create or extend the Sprint 8A manual squat annotation registry."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import pandas as pd


DEFAULT_CUSTOM_LABELS = Path("data/processed/labels/custom_squat_videos_labels.csv")
DEFAULT_AUGMENTED_LABELS = Path("data/processed/labels/augmented_custom_squat_videos_labels.csv")
DEFAULT_V2_LABELS = Path("data/processed/features/squat_video_training_features_v2.csv")
DEFAULT_V3_CANDIDATES = Path("data/processed/labels/squat_training_dataset_v3_candidates.csv")
DEFAULT_OUTPUT = Path("data/processed/labels/manual_rep_annotations.csv")
ANNOTATION_COLUMNS = [
    "video_path",
    "dataset_source",
    "participant_id",
    "session_id",
    "exercise_label",
    "expected_reps",
    "view_type",
    "recording_quality",
    "visible_body_region",
    "camera_position",
    "has_full_body_visible",
    "has_clear_start_position",
    "has_clear_end_position",
    "annotator",
    "annotation_confidence",
    "notes",
]


def normalize_path(value: object) -> str:
    return str(value).strip().replace("\\", "/")


def _truthy(series: pd.Series) -> pd.Series:
    return series.astype(str).str.strip().str.lower().isin({"true", "1", "yes"})


def _read_candidates(path: Path, kind: str) -> list[dict[str, str]]:
    if not path.exists() or path.stat().st_size == 0:
        return []
    data = pd.read_csv(path, dtype=str, keep_default_na=False)
    if kind == "custom":
        required = {"video_path", "label", "is_supported_video"}
        if missing := required.difference(data.columns):
            raise ValueError(f"{path} is missing: " + ", ".join(sorted(missing)))
        data = data[_truthy(data["is_supported_video"])]
        return [
            {
                "video_path": normalize_path(row.video_path),
                "exercise_label": str(row.label).strip(),
                "dataset_source": str(getattr(row, "source_dataset", "custom_squat_videos")).strip()
                or "custom_squat_videos",
            }
            for row in data.itertuples()
        ]
    if kind == "augmented":
        required = {"augmented_video_path", "augmented_label", "safe_for_training"}
        if missing := required.difference(data.columns):
            raise ValueError(f"{path} is missing: " + ", ".join(sorted(missing)))
        data = data[_truthy(data["safe_for_training"])]
        return [
            {
                "video_path": normalize_path(row.augmented_video_path),
                "exercise_label": str(row.augmented_label).strip(),
                "dataset_source": "augmented_custom_squat_videos",
            }
            for row in data.itertuples()
        ]
    if kind == "v2":
        if not {"video_path", "label"}.issubset(data.columns):
            return []
        return [
            {
                "video_path": normalize_path(row.video_path),
                "exercise_label": str(row.label).strip(),
                "dataset_source": str(getattr(row, "source_dataset", "squat_training_v2")).strip()
                or "squat_training_v2",
            }
            for row in data.itertuples()
        ]
    if not {"video_path", "normalized_issue_label"}.issubset(data.columns):
        return []
    return [
        {
            "video_path": normalize_path(row.video_path),
            "exercise_label": str(row.normalized_issue_label).strip(),
            "dataset_source": str(getattr(row, "dataset_source", "squat_training_v3_candidates")).strip()
            or "squat_training_v3_candidates",
            "participant_id": str(getattr(row, "participant_id", "")).strip(),
            "view_type": str(getattr(row, "view_type", "")).strip(),
        }
        for row in data.itertuples()
    ]


def _load_candidates(
    custom_labels_path: Path,
    augmented_labels_path: Path,
    v2_labels_path: Path | None = None,
    v3_candidates_path: Path | None = None,
) -> list[dict[str, str]]:
    candidates: list[dict[str, str]] = []
    for path, kind in (
        (custom_labels_path, "custom"),
        (augmented_labels_path, "augmented"),
        (v2_labels_path, "v2"),
        (v3_candidates_path, "v3"),
    ):
        if path is not None:
            candidates.extend(_read_candidates(path, kind))
    if not candidates:
        raise FileNotFoundError("No readable squat video label or candidate registry was found.")
    # Earlier sources have priority; later registries fill missing metadata only.
    merged: dict[str, dict[str, str]] = {}
    for candidate in candidates:
        key = candidate["video_path"]
        if not key:
            continue
        target = merged.setdefault(key, {})
        for column, value in candidate.items():
            if value and not target.get(column):
                target[column] = value
    return list(merged.values())


def create_annotation_template(
    custom_labels_path: Path,
    augmented_labels_path: Path,
    output_path: Path,
    v2_labels_path: Path | None = None,
    v3_candidates_path: Path | None = None,
) -> tuple[pd.DataFrame, int, int]:
    candidates = _load_candidates(
        custom_labels_path, augmented_labels_path, v2_labels_path, v3_candidates_path
    )
    existing: dict[str, dict[str, str]] = {}
    if output_path.exists() and output_path.stat().st_size:
        previous = pd.read_csv(output_path, dtype=str, keep_default_na=False)
        if "video_path" not in previous.columns:
            raise ValueError("Existing annotation file is missing: video_path")
        for row in previous.to_dict("records"):
            key = normalize_path(row.get("video_path", ""))
            if key and key not in existing:
                existing[key] = {column: str(row.get(column, "")) for column in ANNOTATION_COLUMNS}

    rows: list[dict[str, str]] = []
    added = preserved = 0
    candidate_paths: set[str] = set()
    for candidate in sorted(candidates, key=lambda row: row["video_path"]):
        key = candidate["video_path"]
        candidate_paths.add(key)
        if key in existing:
            row = existing[key].copy()
            preserved += 1
        else:
            row = {column: "" for column in ANNOTATION_COLUMNS}
            added += 1
        row["video_path"] = key
        for column, value in candidate.items():
            if column in ANNOTATION_COLUMNS and value and not row.get(column):
                row[column] = value
        rows.append(row)

    # Preserve reviewed historical rows even if a source registry is temporarily unavailable.
    for key, row in sorted(existing.items()):
        if key not in candidate_paths:
            rows.append(row)
            preserved += 1

    output_path.parent.mkdir(parents=True, exist_ok=True)
    result = pd.DataFrame(rows, columns=ANNOTATION_COLUMNS).fillna("")
    result.to_csv(output_path, index=False)
    return result, added, preserved


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--custom-labels", type=Path, default=DEFAULT_CUSTOM_LABELS)
    parser.add_argument("--augmented-labels", type=Path, default=DEFAULT_AUGMENTED_LABELS)
    parser.add_argument("--v2-labels", type=Path, default=DEFAULT_V2_LABELS)
    parser.add_argument("--v3-candidates", type=Path, default=DEFAULT_V3_CANDIDATES)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        data, added, preserved = create_annotation_template(
            args.custom_labels,
            args.augmented_labels,
            args.output,
            args.v2_labels,
            args.v3_candidates,
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
