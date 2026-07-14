"""Analyze Sprint 7 v2 holdout errors with available Sprint 8A metadata."""

from __future__ import annotations

import argparse
import sys
from collections import Counter
from collections.abc import Callable
from pathlib import Path

import pandas as pd

try:
    from .create_manual_annotation_template import normalize_path
    from .predict_squat_baseline_v2 import DEFAULT_MODEL, predict_rows_v2
except ImportError:  # Direct CLI execution from scripts/.
    from create_manual_annotation_template import normalize_path
    from predict_squat_baseline_v2 import DEFAULT_MODEL, predict_rows_v2


DEFAULT_FEATURES = Path("data/processed/features/squat_video_training_features_v2.csv")
DEFAULT_ANNOTATIONS = Path("data/processed/labels/manual_rep_annotations.csv")
DEFAULT_OUTPUT_CSV = Path("reports/model_reliability/model_error_analysis_v2.csv")
DEFAULT_OUTPUT_MD = Path("reports/model_reliability/model_error_analysis_v2.md")
OUTPUT_COLUMNS = [
    "video_path", "actual_label", "predicted_label", "confidence", "is_error",
    "error_type", "false_negative_for", "false_positive_for", "view_type",
    "recording_quality", "participant_id", "dataset_source", "split",
    "is_low_confidence", "rule_based_label", "ml_rule_disagreement",
]


def _counts(lines: list[str], title: str, values: Counter[str]) -> None:
    lines.extend(["", f"## {title}", ""])
    if values:
        lines.extend(f"- `{key}`: {count}" for key, count in sorted(values.items()))
    else:
        lines.append("- None")


def analyze_model_errors(
    features_path: Path,
    model_path: Path,
    annotations_path: Path,
    output_csv: Path,
    output_md: Path,
    predictor: Callable[[Path, Path, str | None], list[dict[str, object]]] = predict_rows_v2,
) -> tuple[pd.DataFrame, dict[str, object]]:
    if not features_path.exists():
        raise FileNotFoundError(f"V2 feature dataset not found: {features_path}")
    features = pd.read_csv(features_path)
    required = {"video_path", "label", "split", "source_type"}
    if missing := required.difference(features.columns):
        raise ValueError("V2 feature dataset is missing: " + ", ".join(sorted(missing)))
    evaluation = features[
        (features["split"] == "holdout_test") & (features["source_type"] == "real")
    ].copy()
    output_csv.parent.mkdir(parents=True, exist_ok=True)
    if evaluation.empty:
        result = pd.DataFrame(columns=OUTPUT_COLUMNS)
        result.to_csv(output_csv, index=False)
        summary = {"evaluated_rows": 0, "correct_rows": 0, "error_rows": 0,
                   "false_negatives_by_class": {}, "false_positives_by_class": {},
                   "errors_by_view": {}, "errors_by_recording_quality": {},
                   "promotion_supported": False}
        output_md.parent.mkdir(parents=True, exist_ok=True)
        output_md.write_text(
            "# Sprint 8A Model Error Analysis v2\n\n"
            "## Reliability Decision\n\nInsufficient evidence for promotion: no real protected "
            "holdout rows are available. The model remains experimental and the rule-based analyzer remains primary.\n",
            encoding="utf-8",
        )
        return result, summary
    predictions = pd.DataFrame(predictor(model_path, features_path, None))
    if missing := {"video_path", "predicted_label"}.difference(predictions.columns):
        raise ValueError("Prediction output is missing: " + ", ".join(sorted(missing)))
    predictions["video_key"] = predictions["video_path"].map(normalize_path)
    evaluation["video_key"] = evaluation["video_path"].map(normalize_path)
    merged = evaluation.merge(
        predictions[["video_key", "predicted_label", "confidence"]], on="video_key", how="left"
    )
    if merged["predicted_label"].isna().any():
        raise ValueError("Predictions were not available for every holdout video.")

    metadata = pd.DataFrame(columns=["video_key", "view_type", "recording_quality", "participant_id"])
    if annotations_path.exists():
        annotations = pd.read_csv(annotations_path, dtype=str, keep_default_na=False)
        columns = {"video_path", "view_type", "recording_quality", "participant_id"}
        if missing := columns.difference(annotations.columns):
            raise ValueError("Annotation metadata is missing: " + ", ".join(sorted(missing)))
        annotations["video_key"] = annotations["video_path"].map(normalize_path)
        metadata = annotations[["video_key", "view_type", "recording_quality", "participant_id"]].drop_duplicates("video_key")
    merged = merged.merge(metadata, on="video_key", how="left")
    for column in ["view_type", "recording_quality", "participant_id"]:
        merged[column] = merged[column].fillna("").replace("", "unknown")

    dataset_column = "source_dataset" if "source_dataset" in merged.columns else None
    rule_column = next((name for name in ("rule_based_label", "rule_label") if name in merged.columns), None)
    rows = []
    for row in merged.itertuples(index=False):
        is_error = str(row.label) != str(row.predicted_label)
        rows.append({
            "video_path": normalize_path(row.video_path),
            "actual_label": str(row.label),
            "predicted_label": str(row.predicted_label),
            "confidence": row.confidence,
            "is_error": is_error,
            "error_type": "misclassification" if is_error else "correct",
            "false_negative_for": str(row.label) if is_error else "",
            "false_positive_for": str(row.predicted_label) if is_error else "",
            "view_type": row.view_type,
            "recording_quality": row.recording_quality,
            "participant_id": row.participant_id,
            "dataset_source": str(getattr(row, dataset_column, "unknown")) if dataset_column else "unknown",
            "split": str(row.split),
            "is_low_confidence": float(row.confidence) < 0.5,
            "rule_based_label": str(getattr(row, rule_column, "")) if rule_column else "",
            "ml_rule_disagreement": bool(rule_column and str(getattr(row, rule_column, "")) != str(row.predicted_label)),
        })
    result = pd.DataFrame(rows, columns=OUTPUT_COLUMNS)
    result.to_csv(output_csv, index=False)

    errors = result[result["is_error"]]
    false_negatives = Counter(errors["false_negative_for"])
    false_positives = Counter(errors["false_positive_for"])
    errors_by_view = Counter(errors["view_type"])
    errors_by_quality = Counter(errors["recording_quality"])
    summary = {
        "evaluated_rows": len(result),
        "correct_rows": int((~result["is_error"]).sum()),
        "error_rows": len(errors),
        "false_negatives_by_class": dict(false_negatives),
        "false_positives_by_class": dict(false_positives),
        "errors_by_view": dict(errors_by_view),
        "errors_by_recording_quality": dict(errors_by_quality),
        "errors_by_dataset_source": dict(Counter(errors["dataset_source"])),
        "low_confidence_predictions": int(result["is_low_confidence"].sum()),
        "promotion_supported": False,
    }
    lines = [
        "# Sprint 8A Model Error Analysis v2",
        "",
        "## Scope",
        "",
        "This analysis covers only the existing real protected holdout. It is engineering evidence, not clinical validation.",
        "",
        f"- Evaluated videos: {summary['evaluated_rows']}",
        f"- Correct predictions: {summary['correct_rows']}",
        f"- Misclassifications: {summary['error_rows']}",
    ]
    _counts(lines, "False Negatives by Actual Class", false_negatives)
    _counts(lines, "False Positives by Predicted Class", false_positives)
    _counts(lines, "Errors by View Type", errors_by_view)
    _counts(lines, "Errors by Recording Quality", errors_by_quality)
    _counts(lines, "Errors by Dataset Source", Counter(errors["dataset_source"]))
    confusion_lines = [line.rstrip() for line in pd.crosstab(
        result["actual_label"], result["predicted_label"], rownames=["actual"], colnames=["predicted"]
    ).to_string().splitlines()]
    lines.extend(["", "## Confusion Matrix", "", "```", *confusion_lines, "```"])
    lines.extend([
        "",
        "## Reliability Decision",
        "",
        "Insufficient evidence for promotion. The v2 model remains experimental because the current holdout is small, participant grouping is incomplete, manual annotations are incomplete, and class coverage is insufficient.",
        "",
        "The rule-based analyzer remains primary. No diagnostic or treatment claim is supported.",
        "",
    ])
    output_md.write_text("\n".join(line.rstrip() for line in lines), encoding="utf-8")
    return result, summary


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--features", type=Path, default=DEFAULT_FEATURES)
    parser.add_argument("--model", type=Path, default=DEFAULT_MODEL)
    parser.add_argument("--annotations", type=Path, default=DEFAULT_ANNOTATIONS)
    parser.add_argument("--output-csv", type=Path, default=DEFAULT_OUTPUT_CSV)
    parser.add_argument("--output-md", type=Path, default=DEFAULT_OUTPUT_MD)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        _, summary = analyze_model_errors(
            args.features, args.model, args.annotations, args.output_csv, args.output_md
        )
    except Exception as exc:
        print(f"Model error analysis failed: {exc}", file=sys.stderr)
        return 1
    print(f"Analyzed {summary['evaluated_rows']} real holdout videos; errors: {summary['error_rows']}")
    print(f"CSV: {args.output_csv}")
    print(f"Report: {args.output_md}")
    print("Decision: v2 remains experimental; rule-based analysis remains primary.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
