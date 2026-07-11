"""Train small, explainable squat-quality baseline classifiers."""

from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

import joblib
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix,
    precision_recall_fscore_support,
)
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.svm import SVC


MODEL_VERSION = "sprint_5_baseline"
EXPERIMENTAL_WARNING = "Experimental baseline model. Not clinically validated."
DEFAULT_INPUT = Path("data/processed/features/squat_video_training_features.csv")
DEFAULT_MODEL_DIR = Path("models/squat_baseline")
NON_FEATURE_COLUMNS = {"video_path", "label", "split", "source_dataset"}


def build_models(random_state: int = 42) -> dict[str, Pipeline]:
    return {
        "logistic_regression": Pipeline([
            ("imputer", SimpleImputer(strategy="median")),
            ("scaler", StandardScaler()),
            ("classifier", LogisticRegression(max_iter=2000, class_weight="balanced", random_state=random_state)),
        ]),
        "random_forest": Pipeline([
            ("imputer", SimpleImputer(strategy="median")),
            ("classifier", RandomForestClassifier(n_estimators=200, class_weight="balanced", random_state=random_state, n_jobs=1)),
        ]),
        "svc_rbf": Pipeline([
            ("imputer", SimpleImputer(strategy="median")),
            ("scaler", StandardScaler()),
            ("classifier", SVC(class_weight="balanced", probability=True, random_state=random_state)),
        ]),
    }


def calculate_metrics(y_true, y_pred, labels: list[str]) -> dict[str, object]:
    precision, recall, f1, _ = precision_recall_fscore_support(
        y_true, y_pred, average="macro", zero_division=0
    )
    _, _, weighted_f1, _ = precision_recall_fscore_support(
        y_true, y_pred, average="weighted", zero_division=0
    )
    return {
        "accuracy": float(accuracy_score(y_true, y_pred)),
        "macro_precision": float(precision),
        "macro_recall": float(recall),
        "macro_f1": float(f1),
        "weighted_f1": float(weighted_f1),
        "confusion_matrix": confusion_matrix(y_true, y_pred, labels=labels).tolist(),
        "classification_report": classification_report(
            y_true, y_pred, labels=labels, output_dict=True, zero_division=0
        ),
        "y_true": list(y_true),
        "y_pred": list(y_pred),
    }


def train_baselines(
    input_path: Path,
    model_dir: Path,
    random_state: int = 42,
) -> dict[str, object]:
    if not input_path.exists():
        raise FileNotFoundError(f"Training feature CSV not found: {input_path}")
    data = pd.read_csv(input_path)
    required = {"video_path", "label", "split", "source_dataset"}
    missing = required.difference(data.columns)
    if missing:
        raise ValueError(f"Training data is missing columns: {', '.join(sorted(missing))}")
    features = [column for column in data.columns if column not in NON_FEATURE_COLUMNS]
    if not features:
        raise ValueError("Training data has no feature columns.")
    development = data[(data["split"] != "holdout_test") & (data["label"] != "unlabeled")].copy()
    holdout = data[(data["split"] == "holdout_test") & (data["label"] != "unlabeled")].copy()
    if development["label"].nunique() < 2:
        raise ValueError("At least two development classes are required to train a classifier.")
    labels = sorted(data[data["label"] != "unlabeled"]["label"].unique().tolist())
    class_counts = Counter(development["label"])
    min_class_count = min(class_counts.values())
    warnings = [EXPERIMENTAL_WARNING]
    if min_class_count < 2:
        warnings.append(
            "Stratified cross-validation was skipped because at least one development class has fewer than two videos."
        )
    if holdout.empty:
        warnings.append("No protected holdout rows were available; comparative performance metrics were not computed.")
    elif set(labels).difference(holdout["label"].unique()):
        warnings.append("The holdout does not contain every class, so macro metrics and the confusion matrix are incomplete.")

    model_dir.mkdir(parents=True, exist_ok=True)
    artifacts_dir = model_dir / "artifacts"
    artifacts_dir.mkdir(parents=True, exist_ok=True)
    results: dict[str, object] = {}
    trained: dict[str, Pipeline] = {}
    for name, model in build_models(random_state).items():
        model.fit(development[features], development["label"])
        trained[name] = model
        if holdout.empty:
            results[name] = {"evaluation_status": "not_available"}
        else:
            predictions = model.predict(holdout[features])
            results[name] = {
                "evaluation_status": "protected_holdout",
                **calculate_metrics(holdout["label"].tolist(), predictions.tolist(), labels),
            }

    if holdout.empty:
        best_name = sorted(trained)[0]
    else:
        best_name = max(
            trained,
            key=lambda name: (
                results[name]["macro_f1"],
                results[name]["accuracy"],
                name,
            ),
        )
    label_mapping = {label: index for index, label in enumerate(labels)}
    bundle = {
        "model": trained[best_name],
        "model_name": best_name,
        "model_version": MODEL_VERSION,
        "feature_columns": features,
        "label_mapping": label_mapping,
        "warning": EXPERIMENTAL_WARNING,
    }
    joblib.dump(bundle, artifacts_dir / "squat_quality_baseline.pkl")
    (model_dir / "feature_columns.json").write_text(json.dumps(features, indent=2) + "\n", encoding="utf-8")
    (model_dir / "label_mapping.json").write_text(json.dumps(label_mapping, indent=2) + "\n", encoding="utf-8")
    metrics = {
        "model_version": MODEL_VERSION,
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "dataset_rows": int(len(data)),
        "development_rows": int(len(development)),
        "holdout_rows": int(len(holdout)),
        "class_distribution": data["label"].value_counts().sort_index().to_dict(),
        "development_class_distribution": development["label"].value_counts().sort_index().to_dict(),
        "holdout_class_distribution": holdout["label"].value_counts().sort_index().to_dict(),
        "feature_count": len(features),
        "cross_validation": "skipped_insufficient_per_class_samples" if min_class_count < 2 else "not_requested",
        "models": results,
        "best_model": best_name,
        "selection_metric": "protected_holdout_macro_f1" if not holdout.empty else "none",
        "warnings": warnings,
    }
    (model_dir / "metrics.json").write_text(json.dumps(metrics, indent=2) + "\n", encoding="utf-8")
    return metrics


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, default=DEFAULT_INPUT)
    parser.add_argument("--model-dir", type=Path, default=DEFAULT_MODEL_DIR)
    parser.add_argument("--random-state", type=int, default=42)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        metrics = train_baselines(args.input, args.model_dir, args.random_state)
    except Exception as exc:
        print(f"Baseline training failed: {exc}", file=sys.stderr)
        return 1
    print(f"Trained models: {', '.join(metrics['models'])}")
    print(f"Best baseline: {metrics['best_model']}")
    for warning in metrics["warnings"]:
        print(f"WARNING: {warning}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
