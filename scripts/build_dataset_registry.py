"""Build a conservative compatibility registry from the raw dataset audit."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import pandas as pd


DEFAULT_INPUT = Path("reports/dataset_audit/dataset_file_inventory.csv")
DEFAULT_OUTPUT = Path("data/processed/registry/dataset_registry.csv")
DEFAULT_SUMMARY = Path("reports/dataset_audit/dataset_registry_summary.md")
HIGH_PRIORITY = {"custom_videos", "squat_kaggle", "zenodo_squat_dataset"}
ADAPTER_REQUIRED = {
    "uci_physical_therapy_exercises", "ui_prmd", "kimore", "dyntherapy",
    "rehab24_6", "Physical-therapy exercises",
}
REGISTRY_COLUMNS = [
    "dataset_name", "source_path", "status", "data_modality", "file_count",
    "video_count", "image_count", "csv_count", "json_count", "npy_count", "mat_count",
    "annotation_files", "has_labels", "exercise_types", "usable_for_current_squat_mvp",
    "requires_adapter", "priority", "notes",
]


def _bool(value: object) -> bool:
    return str(value).strip().lower() in {"true", "1", "yes"}


def build_registry(inventory_path: Path, output_path: Path, summary_path: Path) -> pd.DataFrame:
    if not inventory_path.exists():
        raise FileNotFoundError(f"Dataset inventory not found: {inventory_path}")
    inventory = pd.read_csv(inventory_path)
    required = {"dataset_name", "dataset_path", "likely_status", "likely_modality", "total_file_count", "video_count", "image_count", "csv_count", "json_count", "npy_count", "mat_count", "annotation_candidate_files", "notes"}
    if missing := required.difference(inventory.columns):
        raise ValueError("Dataset inventory is missing: " + ", ".join(sorted(missing)))
    rows = []
    for row in inventory.itertuples(index=False):
        name = str(row.dataset_name)
        missing = str(row.likely_status) == "missing_or_incomplete" or int(row.total_file_count) == 0
        requires_adapter = name in ADAPTER_REQUIRED or str(row.likely_modality) in {"sensor_timeseries", "skeleton_csv", "mixed", "unknown"}
        video_usable = int(row.video_count) > 0 and str(row.likely_modality) == "video"
        usable = bool(not missing and name in HIGH_PRIORITY and video_usable)
        annotations = str(row.annotation_candidate_files)
        try:
            has_annotation_files = bool(json.loads(annotations))
        except (json.JSONDecodeError, TypeError):
            has_annotation_files = False
        has_labels = has_annotation_files or name == "custom_videos"
        exercise = "bodyweight_squat" if name == "custom_videos" else ("squat" if name in {"squat_kaggle", "zenodo_squat_dataset"} else "unknown")
        status = "missing_or_incomplete" if missing else ("compatible_candidate" if usable else "adapter_required")
        priority = "high" if name in HIGH_PRIORITY else ("medium" if name in ADAPTER_REQUIRED else "low")
        notes = str(row.notes) if pd.notna(row.notes) else ""
        if name in HIGH_PRIORITY and not video_usable:
            notes += " High-priority source is not currently compatible with the squat video pipeline."
        rows.append({
            "dataset_name": name, "source_path": row.dataset_path, "status": status,
            "data_modality": row.likely_modality, "file_count": int(row.total_file_count),
            "video_count": int(row.video_count), "image_count": int(row.image_count),
            "csv_count": int(row.csv_count), "json_count": int(row.json_count),
            "npy_count": int(row.npy_count), "mat_count": int(row.mat_count),
            "annotation_files": annotations, "has_labels": has_labels,
            "exercise_types": exercise, "usable_for_current_squat_mvp": usable,
            "requires_adapter": bool(not missing and (requires_adapter or not usable)),
            "priority": priority, "notes": notes.strip(),
        })
    result = pd.DataFrame(rows, columns=REGISTRY_COLUMNS)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    result.to_csv(output_path, index=False)
    usable_names = result[result.usable_for_current_squat_mvp]["dataset_name"].tolist()
    adapter_names = result[result.requires_adapter]["dataset_name"].tolist()
    missing_names = result[result.status == "missing_or_incomplete"]["dataset_name"].tolist()
    lines = [
        "# Dataset Registry Summary", "",
        f"- Registered datasets: {len(result)}",
        f"- Current squat-video compatible candidates: {len(usable_names)}",
        f"- Require adapters or explicit compatibility work: {len(adapter_names)}",
        f"- Missing/incomplete: {len(missing_names)}", "",
        "## Compatible Candidates", "",
        *([f"- `{name}`" for name in usable_names] or ["- None"]), "",
        "## Adapter Required", "",
        *([f"- `{name}`" for name in adapter_names] or ["- None"]), "",
        "## Missing or Incomplete", "",
        *([f"- `{name}`" for name in missing_names] or ["- None"]), "",
        "Registry compatibility is an engineering gate, not evidence that source labels are clinically equivalent.", "",
    ]
    summary_path.write_text("\n".join(lines), encoding="utf-8")
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, default=DEFAULT_INPUT)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--summary", type=Path, default=DEFAULT_SUMMARY)
    args = parser.parse_args()
    data = build_registry(args.input, args.output, args.summary)
    print(f"Registered {len(data)} datasets. Registry: {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
