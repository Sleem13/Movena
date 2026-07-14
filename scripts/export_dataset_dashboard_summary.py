"""Export a frontend-safe dataset readiness summary from the registry."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import pandas as pd


DEFAULT_INPUT = Path("data/processed/registry/dataset_registry.csv")
DEFAULT_OUTPUT = Path("frontend/src/data/datasetRegistrySummary.json")
FIELDS = ["dataset_name", "status", "modality", "usable_for_current_squat_mvp", "requires_adapter", "file_count", "video_count", "priority", "notes"]


def _bool(value: object) -> bool:
    return str(value).strip().lower() in {"true", "1", "yes"}


def export_dashboard_summary(registry_path: Path, output_path: Path) -> list[dict[str, object]]:
    registry = pd.read_csv(registry_path, keep_default_na=False)
    required = {"dataset_name", "status", "data_modality", "usable_for_current_squat_mvp", "requires_adapter", "file_count", "video_count", "priority", "notes"}
    if missing := required.difference(registry.columns):
        raise ValueError("Dataset registry is missing: " + ", ".join(sorted(missing)))
    rows = []
    for row in registry.itertuples(index=False):
        rows.append({
            "dataset_name": row.dataset_name, "status": row.status, "modality": row.data_modality,
            "usable_for_current_squat_mvp": _bool(row.usable_for_current_squat_mvp),
            "requires_adapter": _bool(row.requires_adapter), "file_count": int(row.file_count),
            "video_count": int(row.video_count), "priority": row.priority, "notes": row.notes,
        })
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(rows, indent=2) + "\n", encoding="utf-8")
    return rows


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, default=DEFAULT_INPUT)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    rows = export_dashboard_summary(args.input, args.output)
    print(f"Exported {len(rows)} dataset summaries to {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
