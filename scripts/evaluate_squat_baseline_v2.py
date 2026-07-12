"""Evaluate the Sprint 7 candidate on the unchanged protected holdout."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import joblib
import numpy as np
import pandas as pd

from train_squat_baseline import calculate_metrics


DEFAULT_INPUT = Path("data/processed/features/squat_video_training_features_v2.csv")
DEFAULT_MODEL = Path("models/squat_baseline_v2/artifacts/squat_quality_baseline_v2.pkl")
DEFAULT_METRICS = Path("models/squat_baseline_v2/metrics.json")
DEFAULT_REPORT = Path("docs/model_evaluation_report_v2.md")
DEFAULT_FIGURE = Path("reports/figures/squat_baseline_v2_confusion_matrix.png")


def evaluate_v2(input_path: Path, model_path: Path, metrics_path: Path, report_path: Path, figure_path: Path):
    bundle = joblib.load(model_path)
    data = pd.read_csv(input_path)
    holdout = data[data["split"] == "holdout_test"]
    if holdout.empty:
        raise ValueError("No protected holdout is available for v2 evaluation.")
    labels = sorted(bundle["label_mapping"])
    predicted = bundle["model"].predict(holdout[bundle["feature_columns"]]).tolist()
    evaluation = calculate_metrics(holdout["label"].tolist(), predicted, labels)
    metrics = json.loads(metrics_path.read_text(encoding="utf-8"))
    metrics["saved_model_evaluation"] = {
        "model_name": bundle["model_name"],
        "evaluation_status": "protected_holdout_preliminary",
        **evaluation,
    }
    metrics_path.write_text(json.dumps(metrics, indent=2) + "\n", encoding="utf-8")

    figure_path.parent.mkdir(parents=True, exist_ok=True)
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from sklearn.metrics import ConfusionMatrixDisplay

    ConfusionMatrixDisplay(
        confusion_matrix=np.asarray(evaluation["confusion_matrix"]), display_labels=labels
    ).plot(cmap="Blues", xticks_rotation=30, colorbar=False)
    plt.title("Sprint 7 candidate - preliminary protected holdout")
    plt.tight_layout()
    plt.savefig(figure_path, dpi=160)
    plt.close()

    report_path.write_text("\n".join([
        "# Model Evaluation Report v2", "", "## Status", "",
        "Preliminary experimental baseline; not clinically validated. The holdout contains three real videos and does not cover every class.", "",
        f"- Candidate: `{bundle['model_name']}`",
        f"- Accuracy: {evaluation['accuracy']:.4f}",
        f"- Macro precision: {evaluation['macro_precision']:.4f}",
        f"- Macro recall: {evaluation['macro_recall']:.4f}",
        f"- Macro F1: {evaluation['macro_f1']:.4f}",
        f"- Weighted F1: {evaluation['weighted_f1']:.4f}",
        f"- Confusion matrix: `{evaluation['confusion_matrix']}`", "",
        "These values are engineering smoke-test evidence. They must not be reported as clinical accuracy or used to enable ML by default.", "",
    ]), encoding="utf-8")
    return evaluation


def parse_args():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, default=DEFAULT_INPUT)
    parser.add_argument("--model", type=Path, default=DEFAULT_MODEL)
    parser.add_argument("--metrics", type=Path, default=DEFAULT_METRICS)
    parser.add_argument("--report", type=Path, default=DEFAULT_REPORT)
    parser.add_argument("--figure", type=Path, default=DEFAULT_FIGURE)
    return parser.parse_args()


def main():
    args = parse_args()
    try:
        result = evaluate_v2(args.input, args.model, args.metrics, args.report, args.figure)
    except Exception as exc:
        print(f"Baseline v2 evaluation failed: {exc}", file=sys.stderr)
        return 1
    print(json.dumps({key: result[key] for key in ["accuracy", "macro_f1", "weighted_f1"]}, indent=2))
    print("WARNING: Metrics are preliminary. Experimental baseline model. Not clinically validated.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
