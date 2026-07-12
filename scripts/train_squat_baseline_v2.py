"""Train Sprint 7 candidate baselines and compare them with Sprint 5."""

from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

import joblib
import pandas as pd

from train_squat_baseline import (
    EXPERIMENTAL_WARNING,
    build_models,
    calculate_metrics,
)


MODEL_VERSION = "sprint_7_baseline_v2"
DEFAULT_INPUT = Path("data/processed/features/squat_video_training_features_v2.csv")
DEFAULT_MODEL_DIR = Path("models/squat_baseline_v2")
DEFAULT_SPRINT5_METRICS = Path("models/squat_baseline/metrics.json")
NON_FEATURE_COLUMNS = {
    "video_path", "label", "split", "source_dataset", "source_type",
    "original_label", "augmented_label",
}


def train_baselines_v2(
    input_path: Path,
    model_dir: Path,
    sprint5_metrics_path: Path = DEFAULT_SPRINT5_METRICS,
    random_state: int = 42,
) -> tuple[dict[str, object], dict[str, object]]:
    data = pd.read_csv(input_path)
    required = {"video_path", "label", "split", "source_type"}
    if missing := required.difference(data.columns):
        raise ValueError("V2 training data is missing: " + ", ".join(sorted(missing)))
    features = [
        column for column in data.columns
        if column not in NON_FEATURE_COLUMNS and pd.api.types.is_numeric_dtype(data[column])
    ]
    development = data[data["split"] != "holdout_test"].copy()
    holdout = data[data["split"] == "holdout_test"].copy()
    if development["label"].nunique() < 2:
        raise ValueError("At least two development classes are required.")
    labels = sorted(data["label"].unique().tolist())
    warnings = [EXPERIMENTAL_WARNING]
    min_count = min(Counter(development["label"]).values())
    if min_count < 2:
        warnings.append("Stratified cross-validation was skipped because a development class has fewer than two videos.")
    if data["source_type"].eq("augmented").any():
        warnings.append("Augmented rows are correlated with real sources and are not independent evidence.")
    if holdout.empty:
        warnings.append("No protected holdout rows were available.")
    elif set(labels).difference(holdout["label"].unique()):
        warnings.append("The protected holdout does not cover every class; metrics are preliminary and incomplete.")

    trained = {}
    results = {}
    for name, model in build_models(random_state).items():
        model.fit(development[features], development["label"])
        trained[name] = model
        if holdout.empty:
            results[name] = {"evaluation_status": "not_available"}
        else:
            predicted = model.predict(holdout[features]).tolist()
            results[name] = {
                "evaluation_status": "protected_holdout_preliminary",
                **calculate_metrics(holdout["label"].tolist(), predicted, labels),
            }
    best_name = sorted(trained)[0] if holdout.empty else max(
        trained,
        key=lambda name: (results[name]["macro_f1"], results[name]["accuracy"], name),
    )
    label_mapping = {label: index for index, label in enumerate(labels)}
    model_dir.mkdir(parents=True, exist_ok=True)
    artifacts = model_dir / "artifacts"
    artifacts.mkdir(parents=True, exist_ok=True)
    joblib.dump({
        "model": trained[best_name], "model_name": best_name,
        "model_version": MODEL_VERSION, "feature_columns": features,
        "label_mapping": label_mapping, "warning": EXPERIMENTAL_WARNING,
    }, artifacts / "squat_quality_baseline_v2.pkl")
    (model_dir / "feature_columns.json").write_text(json.dumps(features, indent=2) + "\n", encoding="utf-8")
    (model_dir / "label_mapping.json").write_text(json.dumps(label_mapping, indent=2) + "\n", encoding="utf-8")
    metrics = {
        "model_version": MODEL_VERSION,
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "dataset_rows": len(data),
        "real_rows": int(data["source_type"].eq("real").sum()),
        "augmented_rows": int(data["source_type"].eq("augmented").sum()),
        "development_rows": len(development),
        "holdout_rows": len(holdout),
        "class_distribution": data["label"].value_counts().sort_index().to_dict(),
        "development_class_distribution": development["label"].value_counts().sort_index().to_dict(),
        "holdout_class_distribution": holdout["label"].value_counts().sort_index().to_dict(),
        "feature_count": len(features),
        "models": results,
        "best_model": best_name,
        "selection_metric": "protected_holdout_macro_f1" if not holdout.empty else "none",
        "metrics_status": "preliminary_small_incomplete_holdout",
        "warnings": warnings,
    }
    (model_dir / "metrics.json").write_text(json.dumps(metrics, indent=2) + "\n", encoding="utf-8")

    sprint5 = json.loads(sprint5_metrics_path.read_text(encoding="utf-8")) if sprint5_metrics_path.exists() else {}
    old_eval = sprint5.get("saved_model_evaluation", {})
    new_eval = results[best_name] if not holdout.empty else {}
    comparison = {
        "sprint5_model": sprint5.get("best_model"),
        "sprint7_model": best_name,
        "sprint5_dataset_rows": sprint5.get("dataset_rows"),
        "sprint7_dataset_rows": len(data),
        "sprint7_augmented_rows": int(data["source_type"].eq("augmented").sum()),
        "accuracy": {"sprint5": old_eval.get("accuracy"), "sprint7": new_eval.get("accuracy")},
        "macro_f1": {"sprint5": old_eval.get("macro_f1"), "sprint7": new_eval.get("macro_f1")},
        "weighted_f1": {"sprint5": old_eval.get("weighted_f1"), "sprint7": new_eval.get("weighted_f1")},
        "decision": "Keep ML optional. Dataset and holdout coverage remain insufficient for default enablement.",
        "warning": EXPERIMENTAL_WARNING,
    }
    for metric in ["accuracy", "macro_f1", "weighted_f1"]:
        old, new = comparison[metric]["sprint5"], comparison[metric]["sprint7"]
        comparison[metric]["delta"] = None if old is None or new is None else new - old
    (model_dir / "comparison_to_sprint5.json").write_text(
        json.dumps(comparison, indent=2) + "\n", encoding="utf-8"
    )
    return metrics, comparison


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, default=DEFAULT_INPUT)
    parser.add_argument("--model-dir", type=Path, default=DEFAULT_MODEL_DIR)
    parser.add_argument("--sprint5-metrics", type=Path, default=DEFAULT_SPRINT5_METRICS)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        metrics, comparison = train_baselines_v2(args.input, args.model_dir, args.sprint5_metrics)
    except Exception as exc:
        print(f"Baseline v2 training failed: {exc}", file=sys.stderr)
        return 1
    print(f"Models trained: {', '.join(metrics['models'])}")
    print(f"Candidate model: {metrics['best_model']}")
    print(comparison["decision"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
