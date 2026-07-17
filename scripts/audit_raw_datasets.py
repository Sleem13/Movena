"""Inventory every raw dataset without interpreting its labels as compatible."""

from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path

import pandas as pd


VIDEO_EXTENSIONS = {".mp4", ".avi", ".mov", ".mkv", ".webm"}
IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".bmp"}
DATA_EXTENSIONS = {".csv", ".tsv", ".xlsx", ".json", ".txt", ".mat", ".npy", ".npz", ".pkl"}
EXPECTED_DATASETS = [
    "custom_videos", "dyntherapy", "kimore", "Physical-therapy exercises",
    "rehab24_6", "squat_kaggle", "uci_physical_therapy_exercises",
    "uco_physical_rehab", "ui_prmd", "zenodo_squat_dataset",
]
FOLDER_ALIASES = {"Physical-therapy exercises": "Pyhsical-therapy exercises"}
OUTPUT_COLUMNS = [
    "dataset_name", "dataset_path", "exists", "total_file_count", "total_size_mb",
    "folder_count", "extension_counts", "video_count", "image_count", "csv_count",
    "json_count", "txt_count", "npy_count", "mat_count", "xml_count",
    "annotation_candidate_files", "sample_files", "likely_modality", "likely_status", "notes",
]


def _rel(path: Path, root: Path) -> str:
    try:
        return str(path.relative_to(root)).replace("\\", "/")
    except ValueError:
        return str(path).replace("\\", "/")


def _likely_modality(name: str, counts: Counter[str]) -> str:
    video = sum(counts[ext] for ext in VIDEO_EXTENSIONS)
    image = sum(counts[ext] for ext in IMAGE_EXTENSIONS)
    key = name.lower()
    if not sum(counts.values()):
        return "missing"
    if video and (image or counts[".npy"] or counts[".npz"] or counts[".mat"] or counts[".pkl"]):
        return "mixed"
    if video:
        return "video"
    if image:
        return "image" if not any(counts[ext] for ext in DATA_EXTENSIONS) else "mixed"
    if "uci" in key:
        return "sensor_timeseries"
    if key in {"dyntherapy", "kimore", "ui_prmd"}:
        return "skeleton_3d"
    if counts[".csv"] or counts[".txt"] or counts[".npy"] or counts[".mat"] or counts[".pkl"]:
        return "unknown"
    return "unknown"


def audit_dataset(name: str, path: Path, raw_root: Path) -> dict[str, object]:
    exists = path.exists() and path.is_dir()
    files = sorted(
        item for item in path.rglob("*")
        if exists and item.is_file() and item.name.lower() != ".gitkeep"
    ) if exists else []
    counts = Counter(item.suffix.lower() or "<no_extension>" for item in files)
    modality = _likely_modality(name, counts)
    annotation_tokens = ("label", "annot", "metadata", "split", "train", "test", "ground", "readme")
    annotations = [
        item for item in files
        if any(token in item.name.lower() for token in annotation_tokens)
        or item.suffix.lower() in {".csv", ".json", ".xml"}
    ][:20]
    incomplete = not files or name == "uco_physical_rehab"
    status = "missing_or_incomplete" if incomplete else (
        "potentially_compatible" if modality == "video" else "adapter_required"
    )
    notes = []
    if not exists:
        notes.append("Dataset folder is missing.")
    elif not files:
        notes.append("Folder contains no dataset files beyond placeholders.")
    if name == "Physical-therapy exercises" and path.name != name:
        notes.append(f"Canonical name mapped to existing folder `{path.name}`.")
    if modality in {"sensor_timeseries", "skeleton_csv", "mixed", "unknown"}:
        notes.append("Do not feed into the squat video pipeline without a dataset-specific adapter.")
    return {
        "dataset_name": name,
        "dataset_path": _rel(path, Path.cwd()),
        "exists": bool(exists),
        "total_file_count": len(files),
        "total_size_mb": round(sum(item.stat().st_size for item in files) / (1024 * 1024), 3),
        "folder_count": sum(1 for item in path.rglob("*") if item.is_dir()) if exists else 0,
        "extension_counts": json.dumps(dict(sorted(counts.items())), sort_keys=True),
        "video_count": sum(counts[ext] for ext in VIDEO_EXTENSIONS),
        "image_count": sum(counts[ext] for ext in IMAGE_EXTENSIONS),
        "csv_count": counts[".csv"], "json_count": counts[".json"],
        "txt_count": counts[".txt"], "npy_count": counts[".npy"],
        "mat_count": counts[".mat"], "xml_count": counts[".xml"],
        "annotation_candidate_files": json.dumps([_rel(item, raw_root) for item in annotations]),
        "sample_files": json.dumps([_rel(item, raw_root) for item in files[:10]]),
        "likely_modality": modality, "likely_status": status, "notes": " ".join(notes),
    }


def audit_raw_datasets(raw_root: Path, inventory_path: Path, summary_path: Path) -> pd.DataFrame:
    actual_names = {item.name for item in raw_root.iterdir() if item.is_dir()} if raw_root.exists() else set()
    rows = []
    represented = set()
    for name in EXPECTED_DATASETS:
        actual = FOLDER_ALIASES.get(name, name)
        rows.append(audit_dataset(name, raw_root / actual, raw_root))
        represented.add(actual)
    for name in sorted(actual_names.difference(represented)):
        rows.append(audit_dataset(name, raw_root / name, raw_root))
    result = pd.DataFrame(rows, columns=OUTPUT_COLUMNS)
    inventory_path.parent.mkdir(parents=True, exist_ok=True)
    result.to_csv(inventory_path, index=False)
    lines = ["# Raw Dataset Audit Summary", "", f"- Dataset entries: {len(result)}", f"- Total files: {int(result.total_file_count.sum())}", f"- Total videos: {int(result.video_count.sum())}", f"- Total images: {int(result.image_count.sum())}", "", "| Dataset | Status | Modality | Files | Videos | Images |", "|---|---|---|---:|---:|---:|"]
    lines.extend(f"| {r.dataset_name} | {r.likely_status} | {r.likely_modality} | {r.total_file_count} | {r.video_count} | {r.image_count} |" for r in result.itertuples())
    lines.extend(["", "Inventory is structural only. Modalities and labels require dataset-specific review before training.", ""])
    summary_path.write_text("\n".join(lines), encoding="utf-8")
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--raw-root", type=Path, default=Path("data/raw"))
    parser.add_argument("--inventory", type=Path, default=Path("reports/dataset_audit/dataset_file_inventory.csv"))
    parser.add_argument("--summary", type=Path, default=Path("reports/dataset_audit/dataset_audit_summary.md"))
    args = parser.parse_args()
    data = audit_raw_datasets(args.raw_root, args.inventory, args.summary)
    print(f"Audited {len(data)} dataset entries. Inventory: {args.inventory}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
