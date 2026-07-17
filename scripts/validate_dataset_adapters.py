"""Validate registered adapters against the unified schema and modality guard."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "backend"))

from app.datasets.modality_guard import check_modality_compatibility
from app.datasets.registry import create_adapter

try:
    from scripts.report_table_utils import dataframe_to_markdown
except ModuleNotFoundError:
    from report_table_utils import dataframe_to_markdown


REQUIRED_FIELDS = {
    "sample_id", "dataset_name", "source_path", "file_path", "modality", "exercise_id",
    "processing_status", "requires_manual_review", "adapter_name", "label_quality",
}
PIPELINE_BY_MODALITY = {
    "video": "video_pose_pipeline",
    "image": "image_pose_pipeline",
    "skeleton_2d": "skeleton_sequence_pipeline",
    "skeleton_3d": "skeleton_sequence_pipeline",
    "sensor_timeseries": "sensor_timeseries_pipeline",
    "tabular_features": "tabular_feature_pipeline",
}


def _resolve_source(source: object) -> Path:
    path = Path(str(source))
    return path if path.is_absolute() else ROOT / path


def validate_adapters(
    registry_path: Path,
    csv_output: Path,
    markdown_output: Path,
    sample_limit: int = 5,
) -> pd.DataFrame:
    registry = pd.read_csv(registry_path)
    rows: list[dict[str, object]] = []

    for entry in registry.to_dict("records"):
        name = str(entry["dataset_name"])
        adapter = create_adapter(name, _resolve_source(entry["source_path"]))
        errors: list[str] = []
        warnings: list[str] = []
        metadata: list[dict[str, object]] = []
        try:
            audit = adapter.audit()
            samples = adapter.list_samples(limit=sample_limit)
            metadata = adapter.export_unified_metadata(limit=sample_limit)
            for sample in metadata:
                missing = REQUIRED_FIELDS - sample.keys()
                if missing:
                    errors.append(f"missing_fields:{','.join(sorted(missing))}")
                modality = str(sample.get("modality", "unknown"))
                pipeline = PIPELINE_BY_MODALITY.get(modality)
                if pipeline:
                    result = check_modality_compatibility(modality, pipeline)
                    if not result.allowed:
                        errors.append(result.reason)
                else:
                    warnings.append(f"manual_modality_review:{modality}")
            if len(metadata) != len(samples):
                errors.append("list/export sample count mismatch")

            if not bool(audit.get("available")):
                status = "missing_dataset"
            elif errors:
                status = "failed"
            elif adapter.requires_manual_mapping:
                status = "needs_manual_mapping"
            elif warnings:
                status = "passed_with_warnings"
            else:
                status = "passed"
        except Exception as exc:  # A single adapter must not abort the validation run.
            audit = {"sample_count": 0, "modality": adapter.modality}
            errors.append(f"{type(exc).__name__}: {exc}")
            warnings = []
            status = "failed"

        rows.append({
            "dataset_name": name,
            "adapter_name": type(adapter).__name__,
            "status": status,
            "modality": audit.get("modality", adapter.modality),
            "sample_count": audit.get("sample_count", 0),
            "checked_sample_count": len(metadata),
            "requires_manual_mapping": adapter.requires_manual_mapping,
            "errors": "; ".join(sorted(set(errors))),
            "warnings": "; ".join(sorted(set(warnings))),
        })

    result = pd.DataFrame(rows)
    csv_output.parent.mkdir(parents=True, exist_ok=True)
    result.to_csv(csv_output, index=False)
    markdown_output.parent.mkdir(parents=True, exist_ok=True)
    markdown_output.write_text(
        "# Dataset Adapter Validation\n\n"
        "Validation checks metadata contracts and modality routing; it does not approve labels or training use.\n\n"
        + dataframe_to_markdown(result)
        + "\n",
        encoding="utf-8",
    )
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--registry", type=Path, default=Path("data/processed/registry/dataset_registry.csv"))
    parser.add_argument("--csv-output", type=Path, default=Path("reports/dataset_audit/dataset_adapter_validation.csv"))
    parser.add_argument("--markdown-output", type=Path, default=Path("reports/dataset_audit/dataset_adapter_validation.md"))
    parser.add_argument("--sample-limit", type=int, default=5)
    args = parser.parse_args()
    result = validate_adapters(args.registry, args.csv_output, args.markdown_output, args.sample_limit)
    print(f"Validated {len(result)} adapters; failures: {int((result.status == 'failed').sum())}")
    return 1 if (result.status == "failed").any() else 0


if __name__ == "__main__":
    raise SystemExit(main())
