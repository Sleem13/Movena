"""Re-evaluate the saved squat baseline on the protected holdout and write evidence."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import joblib
import numpy as np
import pandas as pd

from train_squat_baseline import calculate_metrics


DEFAULT_INPUT = Path("data/processed/features/squat_video_training_features.csv")
DEFAULT_MODEL = Path("models/squat_baseline/artifacts/squat_quality_baseline.pkl")
DEFAULT_METRICS = Path("models/squat_baseline/metrics.json")
DEFAULT_REPORT = Path("docs/model_evaluation_report.md")
DEFAULT_FIGURE = Path("reports/figures/squat_baseline_confusion_matrix.png")


def evaluate_saved_model(
    input_path: Path,
    model_path: Path,
    metrics_path: Path,
    report_path: Path,
    figure_path: Path,
) -> dict[str, object]:
    if not model_path.exists():
        raise FileNotFoundError(f"Saved baseline model not found: {model_path}")
    if not input_path.exists():
        raise FileNotFoundError(f"Training feature CSV not found: {input_path}")
    bundle = joblib.load(model_path)
    data = pd.read_csv(input_path)
    holdout = data[(data["split"] == "holdout_test") & (data["label"] != "unlabeled")]
    if holdout.empty:
        raise ValueError("No protected holdout rows are available for evaluation.")
    features = bundle["feature_columns"]
    labels = sorted(bundle["label_mapping"])
    predictions = bundle["model"].predict(holdout[features]).tolist()
    evaluation = calculate_metrics(holdout["label"].tolist(), predictions, labels)

    metrics = json.loads(metrics_path.read_text(encoding="utf-8")) if metrics_path.exists() else {}
    metrics["saved_model_evaluation"] = {
        "model_name": bundle["model_name"],
        "evaluation_status": "protected_holdout",
        **evaluation,
    }
    metrics_path.parent.mkdir(parents=True, exist_ok=True)
    metrics_path.write_text(json.dumps(metrics, indent=2) + "\n", encoding="utf-8")

    figure_path.parent.mkdir(parents=True, exist_ok=True)
    try:
        import matplotlib

        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
        from sklearn.metrics import ConfusionMatrixDisplay

        display = ConfusionMatrixDisplay(
            confusion_matrix=np.asarray(evaluation["confusion_matrix"]), display_labels=labels
        )
        display.plot(cmap="Blues", xticks_rotation=30, colorbar=False)
        plt.title("Experimental squat baseline - protected holdout")
        plt.tight_layout()
        plt.savefig(figure_path, dpi=160)
        plt.close()
    except ImportError:
        figure_path = Path("not_generated")

    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(
        "\n".join([
            "# Model Evaluation Report",
            "",
            "## Scientific Status",
            "",
            "This is an experimental engineering baseline, not a clinically validated model. The protected holdout contains only three videos and does not contain every class. Metrics are descriptive smoke-test evidence only.",
            "",
            "## Saved Baseline",
            "",
            f"- Model: `{bundle['model_name']}`",
            f"- Holdout rows: {len(holdout)}",
            f"- Accuracy: {evaluation['accuracy']:.4f}",
            f"- Macro precision: {evaluation['macro_precision']:.4f}",
            f"- Macro recall: {evaluation['macro_recall']:.4f}",
            f"- Macro F1: {evaluation['macro_f1']:.4f}",
            f"- Weighted F1: {evaluation['weighted_f1']:.4f}",
            f"- Confusion matrix: `{evaluation['confusion_matrix']}`",
            f"- Figure: `{figure_path}`",
            "",
            "The holdout must not be used to tune thresholds or repeatedly select production behavior. More independently labeled videos per class are required before meaningful validation.",
            "",
        ]),
        encoding="utf-8",
    )
    return evaluation


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, default=DEFAULT_INPUT)
    parser.add_argument("--model", type=Path, default=DEFAULT_MODEL)
    parser.add_argument("--metrics", type=Path, default=DEFAULT_METRICS)
    parser.add_argument("--report", type=Path, default=DEFAULT_REPORT)
    parser.add_argument("--figure", type=Path, default=DEFAULT_FIGURE)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        result = evaluate_saved_model(args.input, args.model, args.metrics, args.report, args.figure)
    except Exception as exc:
        print(f"Baseline evaluation failed: {exc}", file=sys.stderr)
        return 1
    print(json.dumps({key: result[key] for key in ["accuracy", "macro_f1", "weighted_f1"]}, indent=2))
    print("WARNING: Experimental baseline model. Not clinically validated.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
