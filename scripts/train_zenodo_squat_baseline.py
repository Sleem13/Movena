"""Train leakage-aware, experimental Zenodo squat posture baselines."""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path, PurePosixPath

import joblib
import numpy as np
import pandas as pd
from sklearn.metrics import log_loss
from sklearn.model_selection import train_test_split

from train_squat_baseline import EXPERIMENTAL_WARNING, build_models, calculate_metrics
from temperature_scaling import TemperatureScaledClassifier


REPO_ROOT = Path(__file__).resolve().parents[1]
MODEL_VERSION = "zenodo_static_posture_baseline_v2_calibration_audit"
DEFAULT_FEATURES = Path(
    "data/processed/angle_features/zenodo_squat_dataset/zenodo_squat_angle_features.csv"
)
DEFAULT_METADATA = Path("data/processed/labels/zenodo_squat_dataset_labels.csv")
DEFAULT_MODEL_DIR = Path("models/zenodo_squat_baseline")
EXPECTED_LABELS = {"good", "bad_back", "bad_heel"}
NON_FEATURE_COLUMNS = {
    "source_dataset",
    "image_path",
    "label",
    "original_label",
    "source_split",
    "content_sha256",
    "participant_id",
}


def infer_source_split(image_path: str) -> str:
    """Infer a publisher-provided split from portable path text."""
    normalized = image_path.replace("\\", "/")
    parts = [part.lower() for part in PurePosixPath(normalized).parts]
    for candidate in ("train", "test"):
        if candidate in parts:
            return candidate
    return "unknown"


def resolve_image_path(value: str) -> Path:
    path = Path(value)
    if path.is_absolute() or path.exists():
        return path
    return REPO_ROOT / path


def file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as image_file:
        for chunk in iter(lambda: image_file.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def prepare_training_table(features_path: Path, metadata_path: Path) -> tuple[pd.DataFrame, dict[str, object]]:
    """Join pose features to metadata and enforce split leakage checks."""
    if not features_path.exists():
        raise FileNotFoundError(
            f"Zenodo feature CSV not found: {features_path}. Run create_image_angle_features.py first."
        )
    if not metadata_path.exists():
        raise FileNotFoundError(
            f"Zenodo metadata CSV not found: {metadata_path}. Run prepare_zenodo_squat_dataset.py first."
        )

    features = pd.read_csv(features_path)
    metadata = pd.read_csv(metadata_path, dtype=str).fillna("")
    required_features = {"source_dataset", "image_path", "label"}
    required_metadata = {"image_path", "label"}
    if missing := required_features.difference(features.columns):
        raise ValueError("Feature CSV is missing columns: " + ", ".join(sorted(missing)))
    if missing := required_metadata.difference(metadata.columns):
        raise ValueError("Metadata CSV is missing columns: " + ", ".join(sorted(missing)))
    if features["image_path"].duplicated().any():
        raise ValueError("Feature CSV must contain exactly one row per image_path.")
    if metadata["image_path"].duplicated().any():
        raise ValueError("Metadata CSV must contain exactly one row per image_path.")

    metadata_columns = ["image_path"]
    for column in ("label", "source_split", "content_sha256", "participant_id"):
        if column in metadata.columns:
            metadata_columns.append(column)
    table = features.merge(
        metadata[metadata_columns],
        on="image_path",
        how="left",
        validate="one_to_one",
        suffixes=("", "_metadata"),
        indicator=True,
    )
    if not table["_merge"].eq("both").all():
        missing_count = int(table["_merge"].ne("both").sum())
        raise ValueError(f"{missing_count} feature rows have no matching metadata row.")
    table = table.drop(columns=["_merge"])
    if "label_metadata" in table and not table["label"].eq(table["label_metadata"]).all():
        raise ValueError("Feature and metadata labels disagree for at least one image.")
    table = table.drop(columns=["label_metadata"], errors="ignore")

    if "source_split" not in table:
        table["source_split"] = table["image_path"].map(infer_source_split)
    else:
        table["source_split"] = table["source_split"].str.strip().str.lower()
        missing_split = table["source_split"].eq("")
        table.loc[missing_split, "source_split"] = table.loc[missing_split, "image_path"].map(infer_source_split)
    unknown_splits = sorted(set(table["source_split"]) - {"train", "test"})
    if unknown_splits:
        raise ValueError("Every image must belong to the source train or test split.")

    if "content_sha256" not in table:
        table["content_sha256"] = ""
    missing_hash = table["content_sha256"].eq("")
    if missing_hash.any():
        computed = []
        for image_path in table.loc[missing_hash, "image_path"]:
            resolved = resolve_image_path(image_path)
            if not resolved.exists():
                raise FileNotFoundError(f"Cannot hash missing source image: {resolved}")
            computed.append(file_sha256(resolved))
        table.loc[missing_hash, "content_sha256"] = computed

    hash_splits: dict[str, set[str]] = defaultdict(set)
    for digest, split in zip(table["content_sha256"], table["source_split"]):
        hash_splits[digest].add(split)
    cross_split_hashes = sorted(digest for digest, splits in hash_splits.items() if len(splits) > 1)
    if cross_split_hashes:
        raise ValueError(
            f"Detected {len(cross_split_hashes)} exact image duplicate group(s) across train and test."
        )
    duplicate_groups = sum(count > 1 for count in Counter(table["content_sha256"]).values())

    participant_safe = False
    participant_overlap: list[str] = []
    participant_count = 0
    if "participant_id" in table and table["participant_id"].astype(str).str.strip().ne("").all():
        participant_count = int(table["participant_id"].nunique())
        train_participants = set(table.loc[table["source_split"].eq("train"), "participant_id"])
        test_participants = set(table.loc[table["source_split"].eq("test"), "participant_id"])
        participant_overlap = sorted(train_participants & test_participants)
        participant_safe = not participant_overlap

    audit = {
        "source_split_preserved": True,
        "exact_duplicate_groups": duplicate_groups,
        "cross_split_exact_duplicate_groups": len(cross_split_hashes),
        "participant_ids_available": participant_count > 0,
        "participant_count": participant_count,
        "participant_overlap": participant_overlap,
        "participant_grouped_holdout": participant_safe,
    }
    return table, audit


def probability_metrics(
    y_true: list[str],
    probabilities: np.ndarray,
    classes: list[str],
    bins: int = 10,
) -> dict[str, float]:
    """Measure multiclass probability quality without tuning on the result."""
    class_index = {label: index for index, label in enumerate(classes)}
    one_hot = np.zeros_like(probabilities, dtype=float)
    for row_index, label in enumerate(y_true):
        one_hot[row_index, class_index[str(label)]] = 1.0
    predicted_indices = probabilities.argmax(axis=1)
    confidence = probabilities.max(axis=1)
    correctness = np.array(
        [classes[index] == str(actual) for index, actual in zip(predicted_indices, y_true)],
        dtype=float,
    )
    expected_calibration_error = 0.0
    edges = np.linspace(0.0, 1.0, bins + 1)
    for lower, upper in zip(edges[:-1], edges[1:]):
        selected = (confidence > lower) & (confidence <= upper)
        if selected.any():
            expected_calibration_error += float(selected.mean()) * abs(
                float(correctness[selected].mean()) - float(confidence[selected].mean())
            )
    return {
        "multiclass_log_loss": float(log_loss(y_true, probabilities, labels=classes)),
        "multiclass_brier_score": float(np.mean(np.sum((probabilities - one_hot) ** 2, axis=1))),
        "expected_calibration_error_10_bins": expected_calibration_error,
        "mean_confidence": float(confidence.mean()),
    }


def train_zenodo_baselines(
    features_path: Path,
    metadata_path: Path,
    model_dir: Path,
    random_state: int = 42,
) -> dict[str, object]:
    table, audit = prepare_training_table(features_path, metadata_path)
    present_labels = set(table["label"].astype(str))
    if missing_labels := EXPECTED_LABELS.difference(present_labels):
        raise ValueError("Training data is missing expected labels: " + ", ".join(sorted(missing_labels)))

    feature_columns = [
        column
        for column in table.columns
        if column not in NON_FEATURE_COLUMNS and pd.api.types.is_numeric_dtype(table[column])
    ]
    if not feature_columns:
        raise ValueError("Training data contains no numeric posture feature columns.")
    table[feature_columns] = table[feature_columns].replace([float("inf"), float("-inf")], pd.NA)
    development = table[table["source_split"].eq("train")].copy()
    holdout = table[table["source_split"].eq("test")].copy()
    if development.empty or holdout.empty:
        raise ValueError("Both source train and test rows are required.")
    if set(development["label"]) != EXPECTED_LABELS or set(holdout["label"]) != EXPECTED_LABELS:
        raise ValueError("Both source splits must contain all expected posture labels.")

    labels = sorted(EXPECTED_LABELS)
    calibration_rows = max(len(labels), int(round(len(development) * 0.2)))
    fit_development, calibration = train_test_split(
        development,
        test_size=calibration_rows,
        random_state=random_state,
        stratify=development["label"],
    )
    models = build_models(random_state)
    results: dict[str, object] = {}
    for name, model in models.items():
        model.fit(development[feature_columns], development["label"])
        predictions = model.predict(holdout[feature_columns]).tolist()
        evaluation = calculate_metrics(holdout["label"].tolist(), predictions, labels)
        # Per-row predictions do not belong in the summary JSON; keep the report compact.
        evaluation.pop("y_true", None)
        evaluation.pop("y_pred", None)
        results[name] = {
            "evaluation_status": "source_holdout_research_only",
            **evaluation,
        }

    # Calibrate the pre-registered explainable family using development data only.
    uncalibrated_candidate = build_models(random_state)["logistic_regression"]
    uncalibrated_candidate.fit(
        fit_development[feature_columns], fit_development["label"]
    )
    calibrated_candidate = TemperatureScaledClassifier.fit_from_calibration(
        uncalibrated_candidate,
        calibration[feature_columns],
        calibration["label"],
    )
    calibrated_name = "logistic_regression_temperature_scaled"
    models[calibrated_name] = calibrated_candidate
    candidate_predictions = calibrated_candidate.predict(holdout[feature_columns]).tolist()
    candidate_evaluation = calculate_metrics(
        holdout["label"].tolist(), candidate_predictions, labels
    )
    candidate_evaluation.pop("y_true", None)
    candidate_evaluation.pop("y_pred", None)
    uncalibrated_calibration_probabilities = uncalibrated_candidate.predict_proba(
        calibration[feature_columns]
    )
    calibrated_calibration_probabilities = calibrated_candidate.predict_proba(
        calibration[feature_columns]
    )
    uncalibrated_holdout_probabilities = uncalibrated_candidate.predict_proba(
        holdout[feature_columns]
    )
    calibrated_holdout_probabilities = calibrated_candidate.predict_proba(
        holdout[feature_columns]
    )
    results[calibrated_name] = {
        "evaluation_status": "source_holdout_research_only",
        **candidate_evaluation,
        "probability_quality": probability_metrics(
            holdout["label"].tolist(), calibrated_holdout_probabilities, labels
        ),
    }
    calibration_evaluation = {
        "method": "temperature_scaling",
        "temperature": calibrated_candidate.temperature,
        "split_policy": "stratified_20_percent_of_source_train_only",
        "fit_rows": int(len(fit_development)),
        "calibration_rows": int(len(calibration)),
        "fit_class_distribution": fit_development["label"].value_counts().sort_index().to_dict(),
        "calibration_class_distribution": calibration["label"].value_counts().sort_index().to_dict(),
        "calibration_split_probability_quality": {
            "before": probability_metrics(
                calibration["label"].tolist(), uncalibrated_calibration_probabilities, labels
            ),
            "after": probability_metrics(
                calibration["label"].tolist(), calibrated_calibration_probabilities, labels
            ),
        },
        "source_holdout_probability_quality": {
            "before": probability_metrics(
                holdout["label"].tolist(), uncalibrated_holdout_probabilities, labels
            ),
            "after": probability_metrics(
                holdout["label"].tolist(), calibrated_holdout_probabilities, labels
            ),
        },
        "selection_statement": "Temperature scaling was defined before source-test evaluation and was not selected using source-test results.",
    }
    before_quality = calibration_evaluation["source_holdout_probability_quality"]["before"]
    after_quality = calibration_evaluation["source_holdout_probability_quality"]["after"]
    worsened_metrics = [
        metric
        for metric in (
            "multiclass_log_loss",
            "multiclass_brier_score",
            "expected_calibration_error_10_bins",
        )
        if after_quality[metric] > before_quality[metric]
    ]
    calibration_evaluation["worsened_holdout_metrics"] = worsened_metrics
    calibration_evaluation["decision"] = (
        "rejected_holdout_probability_quality_worsened"
        if worsened_metrics
        else "improved_but_not_promoted_without_participant_grouped_validation"
    )
    # A holdout may reject a candidate for safety, but is never used to tune a replacement.
    candidate_name = "logistic_regression"
    warnings = [
        EXPERIMENTAL_WARNING,
        "Static images cannot evaluate repetitions, movement phases, tempo, or temporal quality.",
    ]
    if not audit["participant_grouped_holdout"]:
        warnings.append(
            "Participant identifiers are unavailable or incomplete; the source test split is not proven participant-independent."
        )

    label_mapping = {label: index for index, label in enumerate(labels)}
    model_dir.mkdir(parents=True, exist_ok=True)
    artifacts_dir = model_dir / "artifacts"
    artifacts_dir.mkdir(parents=True, exist_ok=True)
    bundle = {
        "model": models[candidate_name],
        "model_name": candidate_name,
        "model_version": MODEL_VERSION,
        "feature_columns": feature_columns,
        "label_mapping": label_mapping,
        "scope": "static_squat_posture_research_only",
        "warning": EXPERIMENTAL_WARNING,
    }
    joblib.dump(bundle, artifacts_dir / "zenodo_squat_posture_baseline.pkl")
    joblib.dump(
        {
            "model": calibrated_candidate,
            "model_name": calibrated_name,
            "model_version": MODEL_VERSION,
            "feature_columns": feature_columns,
            "label_mapping": label_mapping,
            "scope": "rejected_calibration_experiment_audit_only",
            "warning": EXPERIMENTAL_WARNING,
        },
        artifacts_dir / "zenodo_squat_posture_temperature_scaled_experiment.pkl",
    )
    (model_dir / "feature_columns.json").write_text(
        json.dumps(feature_columns, indent=2) + "\n", encoding="utf-8"
    )
    (model_dir / "label_mapping.json").write_text(
        json.dumps(label_mapping, indent=2) + "\n", encoding="utf-8"
    )
    metrics = {
        "model_version": MODEL_VERSION,
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "dataset_rows": int(len(table)),
        "development_rows": int(len(development)),
        "fit_development_rows": int(len(fit_development)),
        "calibration_rows": int(len(calibration)),
        "holdout_rows": int(len(holdout)),
        "class_distribution": table["label"].value_counts().sort_index().to_dict(),
        "development_class_distribution": development["label"].value_counts().sort_index().to_dict(),
        "holdout_class_distribution": holdout["label"].value_counts().sort_index().to_dict(),
        "feature_count": len(feature_columns),
        "data_leakage_audit": audit,
        "models": results,
        "calibration": calibration_evaluation,
        "candidate_model": candidate_name,
        "selection_policy": "uncalibrated_explainable_candidate_retained; holdout_used_only_to_reject_failed_calibration",
        "promotion_status": "blocked_missing_participant_grouped_holdout",
        "warnings": warnings,
    }
    (model_dir / "metrics.json").write_text(json.dumps(metrics, indent=2) + "\n", encoding="utf-8")
    return metrics


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--features", type=Path, default=DEFAULT_FEATURES)
    parser.add_argument("--metadata", type=Path, default=DEFAULT_METADATA)
    parser.add_argument("--model-dir", type=Path, default=DEFAULT_MODEL_DIR)
    parser.add_argument("--random-state", type=int, default=42)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        metrics = train_zenodo_baselines(
            args.features, args.metadata, args.model_dir, args.random_state
        )
    except Exception as exc:
        print(f"Zenodo baseline training failed: {exc}", file=sys.stderr)
        return 1
    print(f"Trained models: {', '.join(metrics['models'])}")
    print(f"Pre-registered candidate: {metrics['candidate_model']}")
    print(f"Promotion status: {metrics['promotion_status']}")
    for warning in metrics["warnings"]:
        print(f"WARNING: {warning}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
