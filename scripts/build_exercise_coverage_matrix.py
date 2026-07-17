"""Build an exercise/dataset/modality coverage matrix from unified metadata."""

from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd

try:
    from scripts.export_unified_dataset_metadata import is_training_ready_candidate
    from scripts.report_table_utils import dataframe_to_markdown
except ModuleNotFoundError:  # Direct ``python scripts/...`` execution.
    from export_unified_dataset_metadata import is_training_ready_candidate
    from report_table_utils import dataframe_to_markdown


def _quality(values: pd.Series) -> str:
    qualities = {str(value) for value in values.dropna()}
    if "low" in qualities:
        return "low"
    if "medium" in qualities:
        return "medium"
    return "high" if qualities else "unknown"


def _readiness(exercise: str, modality: str, count: int, manual: int, ready: int, app_supported: bool) -> str:
    if exercise == "unknown" or manual:
        return "needs_manual_mapping"
    if modality in {"unknown", "mixed", "missing_or_incomplete"}:
        return "unsupported_modality"
    if count < 5 or ready < 5:
        return "insufficient_samples"
    if not app_supported:
        return "research_only"
    if ready == 0:
        return "app_supported_no_model"
    return "ready_for_exploration"


def build_coverage_matrix(
    unified_samples_path: Path,
    taxonomy_path: Path,
    csv_output: Path,
    markdown_output: Path,
) -> pd.DataFrame:
    samples = pd.read_csv(unified_samples_path)
    taxonomy = pd.read_csv(taxonomy_path).set_index("exercise_id")
    rows: list[dict[str, object]] = []
    if not samples.empty:
        for (exercise, dataset, modality), group in samples.groupby(["exercise_id", "dataset_name", "modality"], dropna=False):
            records = group.to_dict("records")
            manual = int(group["requires_manual_review"].astype(str).str.lower().isin({"true", "1"}).sum())
            ready = sum(is_training_ready_candidate(record) for record in records)
            tax = taxonomy.loc[exercise] if exercise in taxonomy.index else None
            app_supported = bool(tax is not None and str(tax["supported_in_app"]).lower() == "true")
            analyzer = str(tax["rule_based_analyzer_status"]) if tax is not None else "none"
            readiness = _readiness(str(exercise), str(modality), len(group), manual, ready, app_supported)
            rows.append({
                "exercise_id": exercise,
                "dataset_name": dataset,
                "modality": modality,
                "sample_count": len(group),
                "label_quality": _quality(group["label_quality"]),
                "manual_review_count": manual,
                "training_ready_count": ready,
                "app_supported": app_supported,
                "rule_based_analyzer_status": analyzer,
                "ml_dl_readiness": readiness,
                "notes": "Exploration only; app activation and model promotion require separate validation.",
            })
    result = pd.DataFrame(rows)
    csv_output.parent.mkdir(parents=True, exist_ok=True)
    result.to_csv(csv_output, index=False)
    markdown_output.parent.mkdir(parents=True, exist_ok=True)
    markdown_output.write_text(
        "# Exercise Coverage Matrix\n\n"
        "Coverage describes discovered research metadata, not implemented app exercises.\n\n"
        + dataframe_to_markdown(result)
        + "\n",
        encoding="utf-8",
    )
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--samples", type=Path, default=Path("data/processed/registry/unified_samples.csv"))
    parser.add_argument("--taxonomy", type=Path, default=Path("data/processed/registry/exercise_taxonomy.csv"))
    parser.add_argument("--csv-output", type=Path, default=Path("reports/dataset_audit/exercise_coverage_matrix.csv"))
    parser.add_argument("--markdown-output", type=Path, default=Path("reports/dataset_audit/exercise_coverage_matrix.md"))
    args = parser.parse_args()
    result = build_coverage_matrix(args.samples, args.taxonomy, args.csv_output, args.markdown_output)
    print(f"Saved {len(result)} exercise coverage rows to {args.csv_output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
