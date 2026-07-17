"""Export conservative, adapter-normalized metadata for every registered dataset."""

from __future__ import annotations

import argparse
import sys
from collections import Counter
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "backend"))

from app.datasets.adapters.generic_dataset_adapter import GenericDatasetAdapter
from app.datasets.registry import create_adapter


SCHEMA_COLUMNS = [
    "sample_id", "dataset_name", "source_path", "file_path", "modality", "exercise_id",
    "raw_label", "normalized_label", "issue_label", "participant_id", "session_id",
    "view_type", "recording_quality", "duration_sec", "fps", "frame_count",
    "has_manual_rep_count", "expected_reps", "split", "is_augmented", "adapter_name",
    "processing_status", "requires_manual_review", "label_quality", "notes",
]
SUPPORTED_TRAINING_MODALITIES = {
    "video", "image", "skeleton_2d", "skeleton_3d", "sensor_timeseries", "tabular_features",
}


def _truthy(value: object) -> bool:
    return str(value).strip().lower() in {"true", "1", "yes"}


def _resolve_source(source: object) -> Path:
    path = Path(str(source))
    return path if path.is_absolute() else ROOT / path


def is_training_ready_candidate(sample: dict[str, object]) -> bool:
    """Return a discovery-level candidate flag, not model/app readiness."""

    return (
        sample.get("processing_status") == "ready"
        and not _truthy(sample.get("requires_manual_review"))
        and sample.get("label_quality") == "high"
        and sample.get("exercise_id") not in {None, "", "unknown"}
        and sample.get("modality") in SUPPORTED_TRAINING_MODALITIES
    )


def export_unified_metadata(
    registry_path: Path,
    output_path: Path,
    summary_path: Path,
    limit_per_dataset: int | None = None,
    include_research_only: bool = True,
) -> pd.DataFrame:
    registry = pd.read_csv(registry_path)
    rows: list[dict[str, object]] = []
    missing: list[str] = []

    for item in registry.to_dict("records"):
        dataset_name = str(item["dataset_name"])
        status = str(item.get("status", "unknown"))
        if status == "research_only" and not include_research_only:
            continue

        adapter = create_adapter(dataset_name, _resolve_source(item["source_path"]))
        if isinstance(adapter, GenericDatasetAdapter) and type(adapter) is GenericDatasetAdapter:
            adapter.modality = str(item.get("primary_modality", "unknown"))

        samples = adapter.export_unified_metadata(limit=limit_per_dataset)
        if status == "missing_or_incomplete" or not adapter.is_available():
            missing.append(dataset_name)

        registry_requires_review = _truthy(item.get("requires_manual_label_mapping", False))
        for sample in samples:
            sample["requires_manual_review"] = _truthy(sample.get("requires_manual_review")) or registry_requires_review
            if sample["requires_manual_review"] and sample.get("processing_status") == "ready":
                sample["processing_status"] = "needs_manual_mapping"
            sample.setdefault("label_quality", "low" if sample["requires_manual_review"] else "high")
            rows.append(sample)

    output = pd.DataFrame(rows, columns=SCHEMA_COLUMNS)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output.to_csv(output_path, index=False)

    records = output.to_dict("records")
    training_candidates = sum(is_training_ready_candidate(row) for row in records)
    unsupported = sum(row.get("modality") not in SUPPORTED_TRAINING_MODALITIES for row in records)
    manual_review = sum(_truthy(row.get("requires_manual_review")) for row in records)

    def counts(column: str) -> dict[str, int]:
        return dict(Counter(str(row.get(column, "unknown")) for row in records))

    summary_path.parent.mkdir(parents=True, exist_ok=True)
    summary_path.write_text(
        "# Unified Metadata Export Summary\n\n"
        f"- Samples discovered: {len(output)}\n"
        f"- Dataset counts: {counts('dataset_name')}\n"
        f"- Modality counts: {counts('modality')}\n"
        f"- Exercise counts: {counts('exercise_id')}\n"
        f"- Manual-review samples: {manual_review}\n"
        f"- Discovery-level training candidates: {training_candidates}\n"
        f"- Unsupported/mixed/unknown samples: {unsupported}\n"
        f"- Missing/incomplete or empty datasets: {', '.join(sorted(set(missing))) or 'None'}\n\n"
        "A discovery-level candidate is not app-ready or promotion-ready. Unknown labels remain unknown, "
        "and research sources are not merged into a training table.\n",
        encoding="utf-8",
    )
    return output


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--registry", type=Path, default=Path("data/processed/registry/dataset_registry.csv"))
    parser.add_argument("--output", type=Path, default=Path("data/processed/registry/unified_samples.csv"))
    parser.add_argument("--summary", type=Path, default=Path("reports/dataset_audit/unified_metadata_export_summary.md"))
    parser.add_argument("--limit-per-dataset", type=int)
    parser.add_argument("--include-research-only", action="store_true", default=True)
    parser.add_argument("--exclude-research-only", action="store_false", dest="include_research_only")
    args = parser.parse_args()
    data = export_unified_metadata(
        args.registry,
        args.output,
        args.summary,
        limit_per_dataset=args.limit_per_dataset,
        include_research_only=args.include_research_only,
    )
    print(f"Exported {len(data)} sample metadata rows to {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
