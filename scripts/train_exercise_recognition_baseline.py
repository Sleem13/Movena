"""Train a lightweight experimental exercise-recognition baseline when data gates pass."""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

import joblib
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix, f1_score
from sklearn.model_selection import train_test_split
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.svm import SVC


DEFAULT_FEATURES = Path("data/processed/recognition/exercise_recognition_features.csv")
DEFAULT_OUTPUT = Path("models/recognition")
DEFAULT_REGISTRY = Path("data/processed/registry/model_registry.csv")
TRACKS = {
    "video_pose_recognition", "skeleton_sequence_recognition",
    "sensor_timeseries_recognition", "tabular_feature_recognition",
}
MODELS = {"logistic_regression", "random_forest", "svc"}
METADATA_COLUMNS = {
    "sample_id", "dataset_name", "exercise_id", "recognition_track", "participant_id",
    "split", "feature_status", "label", "file_path",
}


def _grouped_split_available(data: pd.DataFrame) -> bool:
    if "participant_id" not in data or "split" not in data:
        return False
    valid = data.dropna(subset=["participant_id", "split"]).copy()
    valid = valid[~valid.participant_id.astype(str).isin({"", "unknown", "nan"})]
    split_values = set(valid.split.astype(str).str.lower())
    evaluation_names = {"holdout", "test"} & split_values
    if "train" not in split_values or not evaluation_names:
        return False
    participant_sets = {
        split: set(group.participant_id.astype(str))
        for split, group in valid.groupby(valid.split.astype(str).str.lower())
    }
    keys = list(participant_sets)
    return all(participant_sets[left].isdisjoint(participant_sets[right]) for i, left in enumerate(keys) for right in keys[i + 1 :])


def validate_training_data(
    data: pd.DataFrame,
    track: str,
    *,
    min_samples_per_class: int = 5,
    allow_non_grouped: bool = False,
) -> dict[str, object]:
    reasons: list[str] = []
    warnings: list[str] = []
    if track not in TRACKS:
        reasons.append(f"unsupported track: {track}")
        filtered = data.iloc[0:0]
    else:
        filtered = data[data["recognition_track"] == track].copy() if "recognition_track" in data else data.iloc[0:0]
    if "feature_status" in filtered:
        filtered = filtered[filtered.feature_status == "available_features"]
    filtered = filtered[filtered.exercise_id.astype(str) != "unknown"] if "exercise_id" in filtered else filtered.iloc[0:0]

    counts = filtered.exercise_id.value_counts().to_dict() if len(filtered) else {}
    if len(counts) < 2:
        reasons.append("at least two known exercise classes are required")
    too_small = {label: count for label, count in counts.items() if count < min_samples_per_class}
    if too_small:
        reasons.append(f"classes below minimum {min_samples_per_class}: {too_small}")

    feature_columns = [
        column for column in filtered.columns
        if column not in METADATA_COLUMNS and pd.api.types.is_numeric_dtype(filtered[column])
    ]
    if not feature_columns:
        reasons.append("no numeric feature columns are available")
    elif filtered[feature_columns].isna().any().any():
        reasons.append("numeric features contain missing values")

    grouped = _grouped_split_available(filtered)
    participant_missing = "participant_id" not in filtered or filtered.participant_id.isna().any() or filtered.participant_id.astype(str).isin({"", "unknown", "nan"}).any()
    if participant_missing:
        warnings.append("participant_id is missing for one or more samples")
    if not grouped:
        if allow_non_grouped:
            warnings.append("participant-grouped evaluation is unavailable; results are exploratory only")
        else:
            reasons.append("participant-grouped train/holdout split is required; use --allow-non-grouped only for exploration")

    return {
        "valid": not reasons,
        "reasons": reasons,
        "warnings": warnings,
        "rows": len(filtered),
        "class_counts": counts,
        "feature_columns": feature_columns,
        "participant_grouped_split": grouped,
        "data": filtered,
    }


def _build_model(name: str):
    if name == "random_forest":
        return RandomForestClassifier(n_estimators=150, random_state=42, class_weight="balanced")
    if name == "logistic_regression":
        return make_pipeline(StandardScaler(), LogisticRegression(max_iter=1000, class_weight="balanced", random_state=42))
    if name == "svc":
        return make_pipeline(StandardScaler(), SVC(kernel="rbf", probability=True, class_weight="balanced", random_state=42))
    raise ValueError(f"Unsupported model: {name}")


def _split(data: pd.DataFrame, grouped: bool) -> tuple[pd.DataFrame, pd.DataFrame]:
    if grouped:
        evaluation = data.split.astype(str).str.lower().isin({"holdout", "test"})
        return data[~evaluation], data[evaluation]
    train, test = train_test_split(data, test_size=0.25, random_state=42, stratify=data.exercise_id)
    return train, test


def _register_model(registry_path: Path, record: dict[str, object]) -> None:
    registry = pd.read_csv(registry_path) if registry_path.exists() else pd.DataFrame()
    for column in record:
        if column not in registry.columns:
            registry[column] = ""
    row = {column: record.get(column, "") for column in registry.columns}
    registry = pd.concat([registry, pd.DataFrame([row])], ignore_index=True)
    registry_path.parent.mkdir(parents=True, exist_ok=True)
    registry.to_csv(registry_path, index=False)


def train_baseline(
    features_path: Path,
    track: str,
    model_name: str,
    output_dir: Path,
    *,
    dry_run: bool = False,
    allow_non_grouped: bool = False,
    min_samples_per_class: int = 5,
    registry_path: Path = DEFAULT_REGISTRY,
) -> dict[str, object]:
    if not features_path.exists():
        return {"valid": False, "trained": False, "reasons": [f"feature table not found: {features_path}"], "warnings": []}
    data = pd.read_csv(features_path)
    validation = validate_training_data(
        data, track, min_samples_per_class=min_samples_per_class, allow_non_grouped=allow_non_grouped
    )
    summary = {key: value for key, value in validation.items() if key != "data"}
    summary.update({"trained": False, "dry_run": dry_run, "model": model_name, "track": track, "automatic_promotion": False})
    if model_name not in MODELS:
        summary["valid"] = False
        summary["reasons"].append(f"unsupported model: {model_name}")
    if dry_run or not summary["valid"]:
        return summary

    filtered = validation["data"]
    feature_columns = validation["feature_columns"]
    train, test = _split(filtered, bool(validation["participant_grouped_split"]))
    model = _build_model(model_name)
    model.fit(train[feature_columns], train.exercise_id)
    predictions = model.predict(test[feature_columns])
    labels = sorted(filtered.exercise_id.unique())
    report = classification_report(test.exercise_id, predictions, labels=labels, output_dict=True, zero_division=0)
    metrics = {
        "accuracy": accuracy_score(test.exercise_id, predictions),
        "macro_f1": f1_score(test.exercise_id, predictions, average="macro", zero_division=0),
        "train_rows": len(train), "test_rows": len(test), "classes": labels,
        "participant_grouped_split": bool(validation["participant_grouped_split"]),
        "experimental": True, "promoted_to_app": False,
    }
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    model_id = f"exercise_recognition_{track}_{model_name}_{timestamp}"
    model_dir = output_dir / model_id
    model_dir.mkdir(parents=True, exist_ok=False)
    joblib.dump(model, model_dir / "model.joblib")
    (model_dir / "metrics.json").write_text(json.dumps(metrics, indent=2), encoding="utf-8")
    (model_dir / "classification_report.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    pd.DataFrame(confusion_matrix(test.exercise_id, predictions, labels=labels), index=labels, columns=labels).to_csv(model_dir / "confusion_matrix.csv")
    metadata = {"model_id": model_id, "model_name": model_name, "track": track, "feature_columns": feature_columns, "classes": labels}
    (model_dir / "metadata.json").write_text(json.dumps(metadata, indent=2), encoding="utf-8")
    (model_dir / "model_card.md").write_text(
        "# Experimental Exercise Recognition Model\n\n"
        f"- Model ID: `{model_id}`\n- Track: `{track}`\n- Classes: {', '.join(labels)}\n"
        f"- Accuracy: {metrics['accuracy']:.4f}\n- Macro F1: {metrics['macro_f1']:.4f}\n\n"
        "Manual exercise selection remains primary. This model is not clinically validated, cannot provide feedback, and is not promoted automatically.\n",
        encoding="utf-8",
    )
    _register_model(registry_path, {
        "model_id": model_id, "model_name": model_name, "exercise_id": "multi_exercise_recognition",
        "modality": track.replace("_recognition", ""), "training_track": track,
        "dataset_sources": ";".join(sorted(filtered.dataset_name.unique())), "version": "v0_experimental",
        "status": "experimental", "macro_f1": metrics["macro_f1"], "accuracy": metrics["accuracy"],
        "per_class_recall_summary": json.dumps({label: report[label]["recall"] for label in labels}),
        "participant_grouped_holdout": metrics["participant_grouped_split"], "manual_annotations_used": False,
        "promoted_to_app": False, "app_usage": "experimental_suggestion_only",
        "warnings": "Manual selection remains primary; no automatic routing; not clinically validated",
        "created_at": datetime.now(timezone.utc).isoformat(),
    })
    summary.update({"trained": True, "model_id": model_id, "output_dir": str(model_dir), "metrics": metrics})
    return summary


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--features-path", type=Path, default=DEFAULT_FEATURES)
    parser.add_argument("--track", choices=sorted(TRACKS), required=True)
    parser.add_argument("--model", choices=sorted(MODELS), default="random_forest")
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--registry", type=Path, default=DEFAULT_REGISTRY)
    parser.add_argument("--min-samples-per-class", type=int, default=5)
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--allow-non-grouped", action="store_true")
    args = parser.parse_args()
    result = train_baseline(
        args.features_path, args.track, args.model, args.output_dir, dry_run=args.dry_run,
        allow_non_grouped=args.allow_non_grouped, min_samples_per_class=args.min_samples_per_class,
        registry_path=args.registry,
    )
    print(json.dumps(result, indent=2, default=str))
    return 0 if args.dry_run or result.get("trained") else 2


if __name__ == "__main__":
    raise SystemExit(main())

