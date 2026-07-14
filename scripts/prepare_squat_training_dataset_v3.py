"""Prepare an audited multi-dataset squat-video candidate registry without training."""

from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd


VIDEO_EXTENSIONS = {".mp4", ".avi", ".mov", ".mkv", ".webm"}
APPROVED_ISSUES = {
    "squat_correct", "squat_knee_valgus", "squat_shallow_depth",
    "squat_trunk_lean", "squat_fast_uncontrolled", "no_valid_squat_detected",
}
DEFAULT_REGISTRY = Path("data/processed/registry/dataset_registry.csv")
DEFAULT_MAPPING = Path("data/processed/registry/exercise_label_mapping.csv")
DEFAULT_CUSTOM_LABELS = Path("data/processed/labels/custom_squat_videos_labels.csv")
DEFAULT_ANNOTATIONS = Path("data/processed/labels/manual_rep_annotations.csv")
DEFAULT_AUGMENTED = Path("data/processed/labels/augmented_custom_squat_videos_labels.csv")
DEFAULT_OUTPUT = Path("data/processed/labels/squat_training_dataset_v3_candidates.csv")
DEFAULT_SUMMARY = Path("reports/dataset_audit/squat_v3_candidate_summary.md")
OUTPUT_COLUMNS = [
    "video_path", "normalized_exercise", "normalized_issue_label", "dataset_source",
    "participant_id", "view_type", "is_augmented", "source_type",
    "compatibility_status", "notes",
]


def normalize_path(value: object) -> str:
    return str(value).strip().replace("\\", "/")


def _bool(value: object) -> bool:
    return str(value).strip().lower() in {"true", "1", "yes"}


def prepare_candidates(
    registry_path: Path,
    mapping_path: Path,
    custom_labels_path: Path,
    annotations_path: Path,
    augmented_path: Path,
    output_path: Path,
    summary_path: Path,
) -> pd.DataFrame:
    registry = pd.read_csv(registry_path, keep_default_na=False)
    mapping = pd.read_csv(mapping_path, keep_default_na=False)
    map_lookup = {
        (str(row.raw_dataset_name), str(row.raw_label)): (str(row.normalized_exercise), str(row.normalized_issue_label), str(row.confidence))
        for row in mapping.itertuples(index=False)
    }
    usable = {
        str(row.dataset_name): Path(str(row.source_path))
        for row in registry.itertuples(index=False)
        if _bool(row.usable_for_current_squat_mvp) and str(row.status) != "missing_or_incomplete"
    }
    annotation_lookup: dict[str, tuple[str, str]] = {}
    if annotations_path.exists():
        annotations = pd.read_csv(annotations_path, dtype=str, keep_default_na=False)
        annotation_lookup = {
            normalize_path(row.video_path): (str(row.participant_id), str(row.view_type))
            for row in annotations.itertuples(index=False)
        }

    rows: list[dict[str, object]] = []
    if "custom_videos" in usable and custom_labels_path.exists():
        labels = pd.read_csv(custom_labels_path, keep_default_na=False)
        for row in labels.itertuples(index=False):
            path = normalize_path(row.video_path)
            if not _bool(row.is_supported_video) or Path(path).suffix.lower() not in VIDEO_EXTENSIONS:
                continue
            mapped = map_lookup.get(("custom_videos", str(row.label)))
            if not mapped or mapped[1] not in APPROVED_ISSUES:
                continue
            participant, view = annotation_lookup.get(path, ("", ""))
            rows.append({
                "video_path": path, "normalized_exercise": mapped[0],
                "normalized_issue_label": mapped[1], "dataset_source": "custom_videos",
                "participant_id": participant, "view_type": view, "is_augmented": False,
                "source_type": "real", "compatibility_status": "candidate_only",
                "notes": "Existing compatible custom squat video; human metadata may remain incomplete.",
            })

    for dataset_name, source_path in usable.items():
        if dataset_name == "custom_videos" or not source_path.exists():
            continue
        for path in sorted(item for item in source_path.rglob("*") if item.is_file() and item.suffix.lower() in VIDEO_EXTENSIONS):
            mapped = map_lookup.get((dataset_name, path.parent.name))
            if not mapped or mapped[1] not in APPROVED_ISSUES:
                continue
            normalized = normalize_path(path)
            participant, view = annotation_lookup.get(normalized, ("", ""))
            rows.append({
                "video_path": normalized, "normalized_exercise": mapped[0],
                "normalized_issue_label": mapped[1], "dataset_source": dataset_name,
                "participant_id": participant, "view_type": view, "is_augmented": False,
                "source_type": "real", "compatibility_status": "candidate_only",
                "notes": "Included only because registry and explicit folder-label mapping both passed.",
            })

    if "custom_videos" in usable and augmented_path.exists():
        augmented = pd.read_csv(augmented_path, keep_default_na=False)
        for row in augmented.itertuples(index=False):
            if not _bool(row.safe_for_training):
                continue
            mapped = map_lookup.get(("custom_videos", str(row.augmented_label)))
            if not mapped or mapped[1] not in APPROVED_ISSUES:
                continue
            path = normalize_path(row.augmented_video_path)
            source = normalize_path(row.source_video_path)
            participant, view = annotation_lookup.get(source, ("", ""))
            rows.append({
                "video_path": path, "normalized_exercise": mapped[0],
                "normalized_issue_label": mapped[1], "dataset_source": "custom_videos",
                "participant_id": participant, "view_type": view, "is_augmented": True,
                "source_type": "augmented", "compatibility_status": "candidate_only",
                "notes": f"Lineage-preserving variant of {source}; not independent evidence.",
            })

    result = pd.DataFrame(rows, columns=OUTPUT_COLUMNS).drop_duplicates("video_path")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    result.to_csv(output_path, index=False)
    incompatible = registry[~registry["dataset_name"].isin(usable)]
    lines = [
        "# Squat Training Dataset v3 Candidate Summary", "",
        "This is a candidate registry only. No v3 model was trained.", "",
        f"- Candidate videos: {len(result)}",
        f"- Real videos: {int((result.source_type == 'real').sum()) if not result.empty else 0}",
        f"- Augmented videos: {int((result.source_type == 'augmented').sum()) if not result.empty else 0}",
        f"- Excluded/incompatible dataset entries: {len(incompatible)}", "",
        "## Candidates by Dataset", "",
    ]
    counts = result.groupby("dataset_source").size().to_dict() if not result.empty else {}
    lines.extend([f"- `{name}`: {count}" for name, count in sorted(counts.items())] or ["- None"])
    lines.extend(["", "## Excluded Registry Entries", ""])
    lines.extend([f"- `{row.dataset_name}`: {row.status}; modality `{row.data_modality}`" for row in incompatible.itertuples(index=False)] or ["- None"])
    lines.extend(["", "Sensor, skeleton, mixed, image-only, missing, and unknown-label sources are excluded by default.", ""])
    summary_path.parent.mkdir(parents=True, exist_ok=True)
    summary_path.write_text("\n".join(lines), encoding="utf-8")
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--registry", type=Path, default=DEFAULT_REGISTRY)
    parser.add_argument("--mapping", type=Path, default=DEFAULT_MAPPING)
    parser.add_argument("--custom-labels", type=Path, default=DEFAULT_CUSTOM_LABELS)
    parser.add_argument("--annotations", type=Path, default=DEFAULT_ANNOTATIONS)
    parser.add_argument("--augmented", type=Path, default=DEFAULT_AUGMENTED)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--summary", type=Path, default=DEFAULT_SUMMARY)
    args = parser.parse_args()
    data = prepare_candidates(args.registry, args.mapping, args.custom_labels, args.annotations, args.augmented, args.output, args.summary)
    print(f"Saved {len(data)} candidate squat videos to {args.output}")
    print("No v3 model was trained.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
