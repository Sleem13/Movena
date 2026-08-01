"""Create confidence-aware error evidence for the Zenodo posture baseline."""

from __future__ import annotations

import argparse
import sys
from collections import Counter
from collections.abc import Callable
from pathlib import Path

import pandas as pd

try:
    from .predict_zenodo_squat_baseline import DEFAULT_MODEL, predict_rows
    from .train_zenodo_squat_baseline import DEFAULT_FEATURES, DEFAULT_METADATA, prepare_training_table
except ImportError:
    from predict_zenodo_squat_baseline import DEFAULT_MODEL, predict_rows
    from train_zenodo_squat_baseline import DEFAULT_FEATURES, DEFAULT_METADATA, prepare_training_table


DEFAULT_OUTPUT_CSV = Path("reports/model_reliability/zenodo_posture_holdout_predictions.csv")
DEFAULT_OUTPUT_MD = Path("reports/model_reliability/zenodo_posture_error_analysis.md")
OUTPUT_COLUMNS = [
    "image_path",
    "actual_label",
    "predicted_label",
    "confidence",
    "confidence_band",
    "is_error",
    "error_pair",
    "false_negative_for",
    "false_positive_for",
    "source_split",
    "source_dataset",
]


def confidence_band(value: float) -> str:
    if value < 0.5:
        return "low_below_0_50"
    if value < 0.75:
        return "medium_0_50_to_0_75"
    return "high_at_least_0_75"


def count_lines(title: str, counts: Counter[str]) -> list[str]:
    lines = ["", f"## {title}", ""]
    lines.extend(f"- `{key}`: {value}" for key, value in sorted(counts.items()))
    if not counts:
        lines.append("- None")
    return lines


def format_metric(value: float | None) -> str:
    return "not_available" if value is None else f"{value:.3f}"


def analyze_errors(
    features_path: Path,
    metadata_path: Path,
    model_path: Path,
    output_csv: Path,
    output_md: Path,
    predictor: Callable[[Path, Path, str | None], list[dict[str, object]]] = predict_rows,
) -> tuple[pd.DataFrame, dict[str, object]]:
    table, leakage_audit = prepare_training_table(features_path, metadata_path)
    holdout = table[table["source_split"].eq("test")].copy()
    predictions = pd.DataFrame(predictor(model_path, features_path, None))
    required_predictions = {"image_path", "predicted_label", "confidence"}
    if missing := required_predictions.difference(predictions.columns):
        raise ValueError("Prediction output is missing: " + ", ".join(sorted(missing)))
    merged = holdout.merge(
        predictions[["image_path", "predicted_label", "confidence"]],
        on="image_path",
        how="left",
        validate="one_to_one",
    )
    if merged["predicted_label"].isna().any() or merged["confidence"].isna().any():
        raise ValueError("Predictions were not available for every source-test image.")

    rows: list[dict[str, object]] = []
    for row in merged.itertuples(index=False):
        actual = str(row.label)
        predicted = str(row.predicted_label)
        confidence = float(row.confidence)
        is_error = actual != predicted
        rows.append(
            {
                "image_path": str(row.image_path),
                "actual_label": actual,
                "predicted_label": predicted,
                "confidence": round(confidence, 6),
                "confidence_band": confidence_band(confidence),
                "is_error": is_error,
                "error_pair": f"{actual} -> {predicted}" if is_error else "correct",
                "false_negative_for": actual if is_error else "",
                "false_positive_for": predicted if is_error else "",
                "source_split": str(row.source_split),
                "source_dataset": str(row.source_dataset),
            }
        )
    result = pd.DataFrame(rows, columns=OUTPUT_COLUMNS)
    output_csv.parent.mkdir(parents=True, exist_ok=True)
    result.to_csv(output_csv, index=False)

    errors = result[result["is_error"]]
    false_negatives = Counter(errors["false_negative_for"])
    false_positives = Counter(errors["false_positive_for"])
    error_pairs = Counter(errors["error_pair"])
    errors_by_confidence = Counter(errors["confidence_band"])
    predictions_by_confidence = Counter(result["confidence_band"])
    selective_performance: dict[str, dict[str, float | int | None]] = {}
    for threshold in (0.5, 0.75, 0.9, 0.95):
        accepted = result[result["confidence"] >= threshold]
        correct = int((~accepted["is_error"]).sum())
        selective_performance[f"at_least_{threshold:.2f}"] = {
            "threshold": threshold,
            "accepted_rows": int(len(accepted)),
            "coverage": float(len(accepted) / len(result)) if len(result) else None,
            "accuracy": float(correct / len(accepted)) if len(accepted) else None,
            "error_rows": int(accepted["is_error"].sum()),
        }
    summary = {
        "evaluated_rows": int(len(result)),
        "correct_rows": int((~result["is_error"]).sum()),
        "error_rows": int(len(errors)),
        "error_rate": float(len(errors) / len(result)) if len(result) else None,
        "mean_confidence": float(result["confidence"].mean()) if len(result) else None,
        "mean_error_confidence": float(errors["confidence"].mean()) if len(errors) else None,
        "false_negatives_by_class": dict(false_negatives),
        "false_positives_by_class": dict(false_positives),
        "error_pairs": dict(error_pairs),
        "predictions_by_confidence": dict(predictions_by_confidence),
        "errors_by_confidence": dict(errors_by_confidence),
        "selective_performance": selective_performance,
        "participant_grouped_holdout": bool(leakage_audit["participant_grouped_holdout"]),
        "promotion_supported": False,
    }

    confusion = pd.crosstab(
        result["actual_label"],
        result["predicted_label"],
        rownames=["actual"],
        colnames=["predicted"],
    )
    lines = [
        "# Zenodo Static Posture Error Analysis",
        "",
        "## Scope",
        "",
        "This report evaluates the retained, uncalibrated logistic-regression candidate on the publisher's source-test split. A separate development-only temperature-scaling experiment was rejected after worsening untouched holdout probability quality. This is engineering evidence for static posture research, not clinical validation.",
        "",
        f"- Evaluated images: {summary['evaluated_rows']}",
        f"- Correct predictions: {summary['correct_rows']}",
        f"- Misclassifications: {summary['error_rows']}",
        f"- Error rate: {format_metric(summary['error_rate'])}",
        f"- Mean prediction confidence: {format_metric(summary['mean_confidence'])}",
        f"- Mean confidence on errors: {format_metric(summary['mean_error_confidence'])}",
    ]
    lines += count_lines("Error Pairs", error_pairs)
    lines += count_lines("False Negatives by Actual Class", false_negatives)
    lines += count_lines("False Positives by Predicted Class", false_positives)
    lines += count_lines("All Predictions by Confidence Band", predictions_by_confidence)
    lines += count_lines("Errors by Confidence Band", errors_by_confidence)
    lines += [
        "",
        "## Selective Performance by Confidence Threshold",
        "",
        "| Threshold | Accepted | Coverage | Accuracy | Errors |",
        "| --- | ---: | ---: | ---: | ---: |",
    ]
    for values in selective_performance.values():
        lines.append(
            f"| {values['threshold']:.2f} | {values['accepted_rows']} | "
            f"{format_metric(values['coverage'])} | {format_metric(values['accuracy'])} | "
            f"{values['error_rows']} |"
        )
    lines += [
        "",
        "## Confusion Matrix",
        "",
        "```",
        *[line.rstrip() for line in confusion.to_string().splitlines()],
        "```",
        "",
        "## Reliability Decision",
        "",
        "Promotion is not supported. Participant identifiers are unavailable, so the source-test split is not proven participant-independent. Static images cannot validate repetitions, movement phases, tempo, or video-level movement quality.",
        "",
        "The uncalibrated model also produces high-confidence mistakes. Confidence thresholds must not be treated as safety guarantees; calibration requires a development-only validation protocol and a separate untouched holdout.",
        "",
        "The model remains offline and research-only; rule-based video analysis remains primary.",
        "",
    ]
    output_md.parent.mkdir(parents=True, exist_ok=True)
    output_md.write_text("\n".join(lines), encoding="utf-8")
    return result, summary


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--features", type=Path, default=DEFAULT_FEATURES)
    parser.add_argument("--metadata", type=Path, default=DEFAULT_METADATA)
    parser.add_argument("--model", type=Path, default=DEFAULT_MODEL)
    parser.add_argument("--output-csv", type=Path, default=DEFAULT_OUTPUT_CSV)
    parser.add_argument("--output-md", type=Path, default=DEFAULT_OUTPUT_MD)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        _, summary = analyze_errors(
            args.features,
            args.metadata,
            args.model,
            args.output_csv,
            args.output_md,
        )
    except Exception as exc:
        print(f"Zenodo error analysis failed: {exc}", file=sys.stderr)
        return 1
    print(
        f"Analyzed {summary['evaluated_rows']} source-test images; "
        f"errors: {summary['error_rows']}"
    )
    print(f"CSV: {args.output_csv}")
    print(f"Report: {args.output_md}")
    print("Decision: research-only; promotion is not supported.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
