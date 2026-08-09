"""Train a video-grouped XGBoost exercise-recognition candidate."""

from __future__ import annotations

import argparse
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd
import sklearn
from sklearn.metrics import accuracy_score, balanced_accuracy_score, classification_report, f1_score
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder


METADATA_COLUMNS = {
    "sample_id", "dataset_name", "exercise_id", "recognition_track", "participant_id",
    "group_id", "split", "feature_status", "label", "file_path",
}


def validate_features(data: pd.DataFrame, min_groups_per_class: int = 5) -> dict[str, object]:
    required = {"exercise_id", "group_id", "feature_status"}
    missing = sorted(required - set(data.columns))
    reasons = [f"missing required columns: {', '.join(missing)}"] if missing else []
    filtered = data[data.feature_status == "available_features"].copy() if not missing else data.iloc[0:0]
    feature_cols = [
        column for column in filtered.columns
        if column not in METADATA_COLUMNS and pd.api.types.is_numeric_dtype(filtered[column])
    ]
    if len(feature_cols) != 40:
        reasons.append(f"expected 40 numeric pose features, found {len(feature_cols)}")
    if filtered[feature_cols].isna().any().any() if feature_cols else False:
        reasons.append("pose features contain missing values")
    group_counts = filtered.groupby("exercise_id").group_id.nunique().to_dict() if len(filtered) else {}
    too_small = {label: count for label, count in group_counts.items() if count < min_groups_per_class}
    if len(group_counts) < 2:
        reasons.append("at least two exercise classes are required")
    if too_small:
        reasons.append(f"classes below minimum {min_groups_per_class} videos: {too_small}")
    return {
        "valid": not reasons,
        "reasons": reasons,
        "rows": len(filtered),
        "feature_columns": feature_cols,
        "video_groups_per_class": group_counts,
        "participant_grouped_holdout": False,
        "promotion_allowed": False,
        "data": filtered,
    }


def train_candidate(
    features_path: Path,
    output_dir: Path,
    *,
    dry_run: bool = False,
    min_groups_per_class: int = 5,
) -> dict[str, object]:
    if not features_path.is_file():
        return {"valid": False, "trained": False, "reasons": [f"feature table not found: {features_path}"]}
    data = pd.read_csv(features_path)
    validation = validate_features(data, min_groups_per_class)
    summary = {key: value for key, value in validation.items() if key != "data"}
    summary.update({"trained": False, "dry_run": dry_run, "model_name": "xgboost", "status": "candidate"})
    if dry_run or not validation["valid"]:
        return summary

    try:
        from xgboost import XGBClassifier
    except ImportError as exc:
        summary["valid"] = False
        summary["reasons"].append("xgboost is not installed; install requirements-ml.txt")
        summary["error"] = str(exc)
        return summary

    filtered = validation["data"].reset_index(drop=True)
    columns = validation["feature_columns"]
    encoder = LabelEncoder()
    encoded = encoder.fit_transform(filtered.exercise_id)
    video_manifest = filtered[["group_id", "exercise_id"]].drop_duplicates()
    if video_manifest.groupby("group_id").exercise_id.nunique().gt(1).any():
        raise ValueError("Each video group must contain exactly one exercise label.")
    train_group_rows, test_group_rows = train_test_split(
        video_manifest,
        test_size=0.2,
        random_state=42,
        stratify=video_manifest.exercise_id,
    )
    train_groups = set(train_group_rows.group_id)
    test_groups = set(test_group_rows.group_id)
    train_indexes = filtered.index[filtered.group_id.isin(train_groups)].to_numpy()
    test_indexes = filtered.index[filtered.group_id.isin(test_groups)].to_numpy()
    if train_groups & test_groups:
        raise RuntimeError("Video-group leakage detected.")

    model = XGBClassifier(
        n_estimators=300, max_depth=6, learning_rate=0.1, subsample=0.8,
        colsample_bytree=0.8, min_child_weight=3, gamma=0.1, reg_alpha=0.05,
        reg_lambda=1.0, objective="multi:softprob", eval_metric="mlogloss",
        random_state=42, n_jobs=-1,
    )
    # Give every source video equal total weight so longer clips do not dominate training.
    train_frame_counts = filtered.loc[train_indexes].group_id.value_counts()
    sample_weight = filtered.loc[train_indexes].group_id.map(lambda group: 1.0 / train_frame_counts[group])
    model.fit(filtered.loc[train_indexes, columns], encoded[train_indexes], sample_weight=sample_weight)
    predicted_indexes = model.predict(filtered.loc[test_indexes, columns]).astype(int)
    predicted = encoder.inverse_transform(predicted_indexes)
    actual = filtered.loc[test_indexes].exercise_id.to_numpy()
    labels = encoder.classes_.tolist()
    report = classification_report(actual, predicted, labels=labels, output_dict=True, zero_division=0)
    metrics = {
        "accuracy": accuracy_score(actual, predicted),
        "balanced_accuracy": balanced_accuracy_score(actual, predicted),
        "macro_f1": f1_score(actual, predicted, average="macro", zero_division=0),
        "per_class_recall": {label: report[label]["recall"] for label in labels},
        "train_rows": len(train_indexes), "test_rows": len(test_indexes),
        "train_video_groups": len(train_groups), "test_video_groups": len(test_groups),
        "video_group_leakage": False, "participant_grouped_holdout": False,
        "validation_scope": "stratified_video_group_holdout",
        "deployment_status": "development_candidate",
    }
    model_id = f"exercise_pose_xgb_{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')}"
    model_dir = output_dir / model_id
    model_dir.mkdir(parents=True, exist_ok=False)
    model.save_model(model_dir / "model.json")
    metadata = {
        "model_id": model_id, "model_name": "xgboost_pose_classifier",
        "artifact_format": "xgboost_json", "track": "video_pose_recognition",
        "feature_columns": columns, "classes": labels, "status": "candidate",
        "promoted_to_app": False, "requires_manual_confirmation": True,
        "participant_grouped_holdout": False,
        "validation_scope": "stratified_video_group_holdout",
        "source_features_sha256": hashlib.sha256(features_path.read_bytes()).hexdigest(),
        "training_dependencies": {
            "pandas": pd.__version__, "scikit_learn": sklearn.__version__,
            "xgboost": __import__("xgboost").__version__,
        },
    }
    (model_dir / "metadata.json").write_text(json.dumps(metadata, indent=2), encoding="utf-8")
    (model_dir / "metrics.json").write_text(json.dumps(metrics, indent=2), encoding="utf-8")
    (model_dir / "classification_report.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    split_manifest = video_manifest.copy()
    split_manifest["split"] = split_manifest.group_id.map(
        lambda group: "train" if group in train_groups else "holdout"
    )
    split_manifest.sort_values(["split", "exercise_id", "group_id"]).to_csv(
        model_dir / "split_manifest.csv", index=False
    )
    (model_dir / "model_card.md").write_text(
        "# Exercise Pose Classifier — Development Candidate\n\n"
        "This video-grouped model suggests an exercise label and requires manual confirmation. "
        "Its holdout contains unseen videos, but participant identities are unavailable, so the measured "
        "results are not proof of unseen-person or clinical performance. It does not produce form feedback.\n",
        encoding="utf-8",
    )
    summary.update({"trained": True, "model_id": model_id, "output_dir": str(model_dir), "metrics": metrics})
    return summary


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--features-path", type=Path, default=Path("data/processed/recognition/exercise_pose_features.csv"))
    parser.add_argument("--output-dir", type=Path, default=Path("models/recognition"))
    parser.add_argument("--min-groups-per-class", type=int, default=5)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    result = train_candidate(args.features_path, args.output_dir, dry_run=args.dry_run, min_groups_per_class=args.min_groups_per_class)
    print(json.dumps(result, indent=2, default=str))
    return 0 if args.dry_run or result.get("trained") else 2


if __name__ == "__main__":
    raise SystemExit(main())
