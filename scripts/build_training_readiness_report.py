"""Report research training readiness without authorizing model or app use."""

from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd

try:
    from scripts.export_unified_dataset_metadata import is_training_ready_candidate
    from scripts.report_table_utils import dataframe_to_markdown
except ModuleNotFoundError:
    from export_unified_dataset_metadata import is_training_ready_candidate
    from report_table_utils import dataframe_to_markdown


def _bool_series(series: pd.Series) -> pd.Series:
    return series.astype(str).str.lower().isin({"true", "1", "yes"})


def build_training_readiness_report(
    unified_samples_path: Path,
    dataset_registry_path: Path,
    taxonomy_path: Path,
    csv_output: Path,
    markdown_output: Path,
    model_registry_path: Path | None = None,
) -> pd.DataFrame:
    samples = pd.read_csv(unified_samples_path)
    # Read these inputs to fail early when governance files are absent or malformed.
    pd.read_csv(dataset_registry_path)
    pd.read_csv(taxonomy_path)
    if model_registry_path and model_registry_path.exists():
        pd.read_csv(model_registry_path)

    rows: list[dict[str, object]] = []
    if not samples.empty:
        for (exercise, modality), group in samples.groupby(["exercise_id", "modality"], dropna=False):
            records = group.to_dict("records")
            ready = sum(is_training_ready_candidate(record) for record in records)
            manual = int(_bool_series(group["requires_manual_review"]).sum())
            participants = group["participant_id"].dropna().astype(str)
            participants = participants[~participants.isin({"", "unknown", "nan"})]
            participant_count = participants.nunique()
            assigned_splits = set(group["split"].dropna().astype(str)) - {"", "unassigned", "unknown"}
            grouped_evaluation = participant_count >= 2 and bool({"train", "validation", "holdout"} <= assigned_splits)
            labels_known = str(exercise) != "unknown" and manual == 0
            enough = ready >= 20
            classic_modality = modality in {"video", "image", "tabular_features"}
            sequence_modality = modality in {"skeleton_2d", "skeleton_3d"}
            sensor_modality = modality == "sensor_timeseries"

            blockers: list[str] = []
            if not labels_known:
                blockers.append("unknown_or_unreviewed_labels")
            if not enough:
                blockers.append("insufficient_reviewed_samples")
            if not grouped_evaluation:
                blockers.append("participant_grouped_train_validation_holdout_missing")
            if modality in {"mixed", "unknown", "missing_or_incomplete"}:
                blockers.append("unsupported_or_unresolved_modality")

            can_train = labels_known and enough and grouped_evaluation
            quality_values = set(group["label_quality"].dropna().astype(str))
            quality = "low" if "low" in quality_values else "medium" if "medium" in quality_values else "high"
            rows.append({
                "exercise_id": exercise,
                "modality": modality,
                "total_samples": len(group),
                "training_ready_samples": ready,
                "manual_review_samples": manual,
                "participant_count": participant_count,
                "dataset_sources": ";".join(sorted(group["dataset_name"].astype(str).unique())),
                "label_quality": quality,
                "can_train_classic_ml": bool(can_train and classic_modality),
                "can_train_sequence_dl": bool(can_train and sequence_modality),
                "can_train_sensor_model": bool(can_train and sensor_modality),
                "blockers": ";".join(blockers) or "none",
                "recommended_next_action": (
                    "Create reviewed label mappings and participant-grouped splits."
                    if blockers else "Run bounded exploratory evaluation; do not promote automatically."
                ),
            })

    result = pd.DataFrame(rows)
    csv_output.parent.mkdir(parents=True, exist_ok=True)
    result.to_csv(csv_output, index=False)
    markdown_output.parent.mkdir(parents=True, exist_ok=True)
    markdown_output.write_text(
        "# Training Readiness Report\n\n"
        "Training readiness is not app readiness or clinical validation. Rule-based analyzers remain primary.\n\n"
        + dataframe_to_markdown(result)
        + "\n",
        encoding="utf-8",
    )
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--samples", type=Path, default=Path("data/processed/registry/unified_samples.csv"))
    parser.add_argument("--dataset-registry", type=Path, default=Path("data/processed/registry/dataset_registry.csv"))
    parser.add_argument("--taxonomy", type=Path, default=Path("data/processed/registry/exercise_taxonomy.csv"))
    parser.add_argument("--model-registry", type=Path, default=Path("data/processed/registry/model_registry.csv"))
    parser.add_argument("--csv-output", type=Path, default=Path("reports/model_reliability/training_readiness_report.csv"))
    parser.add_argument("--markdown-output", type=Path, default=Path("reports/model_reliability/training_readiness_report.md"))
    args = parser.parse_args()
    result = build_training_readiness_report(
        args.samples, args.dataset_registry, args.taxonomy, args.csv_output, args.markdown_output, args.model_registry
    )
    print(f"Saved {len(result)} training-readiness rows to {args.csv_output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
