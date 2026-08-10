"""Train a video-sequence GRU exercise-recognition candidate."""

from __future__ import annotations

import argparse
import hashlib
import json
import random
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
import sklearn
from sklearn.metrics import (
    accuracy_score,
    balanced_accuracy_score,
    classification_report,
    confusion_matrix,
    f1_score,
)
from sklearn.model_selection import train_test_split


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from models.dl.exercise_sequence_classifier import ExerciseSequenceClassifier  # noqa: E402
from scripts.train_exercise_pose_xgboost import validate_features  # noqa: E402


DEFAULT_FEATURES = Path("data/processed/recognition/exercise_pose_features.csv")
DEFAULT_OUTPUT = Path("models/recognition")


def _resample_sequence(values: np.ndarray, sequence_length: int) -> np.ndarray:
    if len(values) == 0:
        raise ValueError("Cannot resample an empty video sequence.")
    if len(values) == 1:
        return np.repeat(values, sequence_length, axis=0).astype(np.float32)
    source = np.linspace(0.0, 1.0, len(values))
    target = np.linspace(0.0, 1.0, sequence_length)
    return np.stack(
        [np.interp(target, source, values[:, column]) for column in range(values.shape[1])],
        axis=1,
    ).astype(np.float32)


def build_video_sequences(
    data: pd.DataFrame,
    feature_columns: list[str],
    sequence_length: int = 64,
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Convert ordered frame rows into one fixed-length sample per video."""

    if sequence_length < 2:
        raise ValueError("sequence_length must be at least 2")
    sequences: list[np.ndarray] = []
    labels: list[str] = []
    groups: list[str] = []
    for group_id, frames in data.groupby("group_id", sort=False):
        group_labels = frames.exercise_id.astype(str).unique()
        if len(group_labels) != 1:
            raise ValueError(f"Video group {group_id} contains multiple exercise labels.")
        values = frames[feature_columns].to_numpy(dtype=np.float32)
        if not np.isfinite(values).all():
            raise ValueError(f"Video group {group_id} contains non-finite pose features.")
        sequences.append(_resample_sequence(values, sequence_length))
        labels.append(group_labels[0])
        groups.append(str(group_id))
    return np.stack(sequences), np.asarray(labels), np.asarray(groups)


def stratified_video_split(
    labels: np.ndarray,
    *,
    test_size: float = 0.2,
    validation_size: float = 0.2,
    random_state: int = 42,
) -> dict[str, np.ndarray]:
    """Return disjoint video indexes with every class represented in each split."""

    indexes = np.arange(len(labels))
    development, test = train_test_split(
        indexes, test_size=test_size, random_state=random_state, stratify=labels
    )
    relative_validation_size = validation_size / (1.0 - test_size)
    train, validation = train_test_split(
        development,
        test_size=relative_validation_size,
        random_state=random_state,
        stratify=labels[development],
    )
    return {"train": train, "validation": validation, "holdout": test}


def _classification_metrics(actual: np.ndarray, predicted: np.ndarray, classes: list[str]) -> dict[str, Any]:
    return {
        "accuracy": float(accuracy_score(actual, predicted)),
        "balanced_accuracy": float(balanced_accuracy_score(actual, predicted)),
        "macro_f1": float(f1_score(actual, predicted, average="macro", zero_division=0)),
        "confusion_matrix": confusion_matrix(actual, predicted, labels=classes).tolist(),
        "classification_report": classification_report(
            actual, predicted, labels=classes, output_dict=True, zero_division=0
        ),
    }


def calibrated_probabilities(logits: np.ndarray, temperature: float = 1.0) -> np.ndarray:
    """Convert logits to probabilities using a positive calibration temperature."""

    if temperature <= 0:
        raise ValueError("temperature must be positive")
    scaled = np.asarray(logits, dtype=np.float64) / temperature
    scaled -= scaled.max(axis=1, keepdims=True)
    exponentials = np.exp(scaled)
    return exponentials / exponentials.sum(axis=1, keepdims=True)


def negative_log_likelihood(logits: np.ndarray, targets: np.ndarray, temperature: float = 1.0) -> float:
    probabilities = calibrated_probabilities(logits, temperature)
    selected = probabilities[np.arange(len(targets)), np.asarray(targets, dtype=int)]
    return float(-np.log(np.clip(selected, 1e-12, 1.0)).mean())


def expected_calibration_error(
    probabilities: np.ndarray, targets: np.ndarray, bins: int = 10
) -> float:
    """Return top-label expected calibration error using equal-width bins."""

    if bins < 1:
        raise ValueError("bins must be positive")
    confidences = probabilities.max(axis=1)
    correct = probabilities.argmax(axis=1) == np.asarray(targets)
    error = 0.0
    boundaries = np.linspace(0.0, 1.0, bins + 1)
    for index in range(bins):
        lower, upper = boundaries[index], boundaries[index + 1]
        members = (confidences > lower) & (confidences <= upper)
        if members.any():
            error += members.mean() * abs(correct[members].mean() - confidences[members].mean())
    return float(error)


def fit_temperature(logits: np.ndarray, targets: np.ndarray) -> float:
    """Fit temperature scaling on validation data with a deterministic log grid."""

    candidates = np.geomspace(0.25, 5.0, 800)
    losses = np.asarray([negative_log_likelihood(logits, targets, value) for value in candidates])
    return float(candidates[int(losses.argmin())])


def select_confidence_threshold(
    probabilities: np.ndarray,
    targets: np.ndarray,
    *,
    target_precision: float = 0.85,
    minimum_coverage: float = 0.25,
) -> dict[str, float | int]:
    """Select the broadest validation subset meeting the requested selective precision."""

    confidences = probabilities.max(axis=1)
    correct = probabilities.argmax(axis=1) == np.asarray(targets)
    minimum_count = max(1, int(np.ceil(len(targets) * minimum_coverage)))
    choices: list[tuple[int, float, float]] = []
    for threshold in np.unique(confidences):
        accepted = confidences >= threshold
        count = int(accepted.sum())
        precision = float(correct[accepted].mean())
        if count >= minimum_count and precision >= target_precision:
            choices.append((count, float(threshold), precision))
    if choices:
        count, threshold, precision = max(choices, key=lambda item: (item[0], -item[1]))
    else:
        order = np.argsort(confidences)[::-1][:minimum_count]
        count = minimum_count
        threshold = float(confidences[order[-1]])
        precision = float(correct[order].mean())
    return {
        "threshold": threshold,
        "accepted_count": count,
        "coverage": count / len(targets),
        "selective_accuracy": precision,
        "target_precision": target_precision,
        "minimum_coverage": minimum_coverage,
    }


def train_candidate(
    features_path: Path,
    output_dir: Path,
    *,
    epochs: int = 80,
    batch_size: int = 16,
    sequence_length: int = 64,
    hidden_size: int = 64,
    learning_rate: float = 1e-3,
    patience: int = 12,
    device_request: str = "auto",
    dry_run: bool = False,
) -> dict[str, Any]:
    if not features_path.is_file():
        return {"valid": False, "trained": False, "reasons": [f"feature table not found: {features_path}"]}
    if min(epochs, batch_size, hidden_size, patience) < 1 or sequence_length < 2:
        return {"valid": False, "trained": False, "reasons": ["training parameters must be positive"]}

    data = pd.read_csv(features_path)
    validation = validate_features(data)
    summary = {key: value for key, value in validation.items() if key != "data"}
    summary.update({
        "trained": False,
        "dry_run": dry_run,
        "model_name": "bidirectional_gru_attention",
        "status": "candidate",
        "sequence_length": sequence_length,
    })
    if not validation["valid"]:
        return summary

    filtered = validation["data"].reset_index(drop=True)
    columns = validation["feature_columns"]
    sequences, labels, groups = build_video_sequences(filtered, columns, sequence_length)
    classes = sorted(np.unique(labels).tolist())
    split_indexes = stratified_video_split(labels)
    summary["video_sequences"] = len(sequences)
    summary["split_video_counts"] = {name: len(indexes) for name, indexes in split_indexes.items()}
    if dry_run:
        return summary

    try:
        import torch
        from torch.utils.data import DataLoader, TensorDataset
    except ImportError as exc:
        summary.update(valid=False, reasons=["PyTorch is not installed; install requirements-ml.txt"], error=str(exc))
        return summary

    random.seed(42)
    np.random.seed(42)
    torch.manual_seed(42)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(42)
    if device_request not in {"auto", "cpu", "cuda"}:
        raise ValueError("device_request must be auto, cpu, or cuda")
    use_cuda = torch.cuda.is_available() and device_request in {"auto", "cuda"}
    device = torch.device("cuda" if use_cuda else "cpu")
    device_warning = "CUDA was unavailable; CPU was used." if device_request == "cuda" and not use_cuda else None

    train_indexes = split_indexes["train"]
    feature_mean = sequences[train_indexes].reshape(-1, sequences.shape[-1]).mean(axis=0)
    feature_std = sequences[train_indexes].reshape(-1, sequences.shape[-1]).std(axis=0)
    feature_std[feature_std < 1e-6] = 1.0
    normalized = ((sequences - feature_mean) / feature_std).astype(np.float32)
    class_to_index = {label: index for index, label in enumerate(classes)}
    encoded = np.asarray([class_to_index[label] for label in labels], dtype=np.int64)

    def loader_for(indexes: np.ndarray, shuffle: bool) -> DataLoader:
        dataset = TensorDataset(
            torch.from_numpy(normalized[indexes]), torch.from_numpy(encoded[indexes])
        )
        generator = torch.Generator().manual_seed(42)
        return DataLoader(
            dataset, batch_size=batch_size, shuffle=shuffle, num_workers=0, generator=generator
        )

    train_loader = loader_for(train_indexes, True)
    validation_loader = loader_for(split_indexes["validation"], False)
    holdout_loader = loader_for(split_indexes["holdout"], False)
    model = ExerciseSequenceClassifier(
        input_size=len(columns), hidden_size=hidden_size, num_classes=len(classes)
    ).to(device)
    counts = np.bincount(encoded[train_indexes], minlength=len(classes)).astype(np.float32)
    class_weights = counts.sum() / np.maximum(counts * len(classes), 1.0)
    loss_function = torch.nn.CrossEntropyLoss(weight=torch.from_numpy(class_weights).to(device))
    optimizer = torch.optim.AdamW(model.parameters(), lr=learning_rate, weight_decay=1e-4)

    def predict(loader: DataLoader) -> tuple[np.ndarray, np.ndarray, float]:
        model.eval()
        actual_parts: list[np.ndarray] = []
        logit_parts: list[np.ndarray] = []
        total_loss = 0.0
        batches = 0
        with torch.no_grad():
            for inputs, targets in loader:
                inputs, targets = inputs.to(device), targets.to(device)
                logits = model(inputs)
                total_loss += float(loss_function(logits, targets).detach().cpu())
                batches += 1
                actual_parts.append(targets.cpu().numpy())
                logit_parts.append(logits.cpu().numpy())
        return np.concatenate(actual_parts), np.concatenate(logit_parts), total_loss / max(batches, 1)

    best_state: dict[str, Any] | None = None
    best_validation_f1 = -1.0
    epochs_without_improvement = 0
    history: list[dict[str, float | int]] = []
    for epoch in range(1, epochs + 1):
        model.train()
        train_loss = 0.0
        batches = 0
        for inputs, targets in train_loader:
            inputs, targets = inputs.to(device), targets.to(device)
            optimizer.zero_grad(set_to_none=True)
            loss = loss_function(model(inputs), targets)
            loss.backward()
            torch.nn.utils.clip_grad_norm_(model.parameters(), max_norm=1.0)
            optimizer.step()
            train_loss += float(loss.detach().cpu())
            batches += 1
        validation_actual, validation_logits, validation_loss = predict(validation_loader)
        validation_predicted = validation_logits.argmax(axis=1)
        validation_f1 = float(f1_score(validation_actual, validation_predicted, average="macro", zero_division=0))
        history.append({
            "epoch": epoch,
            "train_loss": train_loss / max(batches, 1),
            "validation_loss": validation_loss,
            "validation_macro_f1": validation_f1,
        })
        if validation_f1 > best_validation_f1 + 1e-6:
            best_validation_f1 = validation_f1
            best_state = {name: value.detach().cpu().clone() for name, value in model.state_dict().items()}
            epochs_without_improvement = 0
        else:
            epochs_without_improvement += 1
            if epochs_without_improvement >= patience:
                break

    if best_state is None:
        raise RuntimeError("Training did not produce a model state.")
    model.load_state_dict(best_state)
    model.to(device)
    validation_actual, validation_logits, _ = predict(validation_loader)
    holdout_actual, holdout_logits, holdout_loss = predict(holdout_loader)
    temperature = fit_temperature(validation_logits, validation_actual)
    validation_probabilities = calibrated_probabilities(validation_logits, temperature)
    holdout_probabilities = calibrated_probabilities(holdout_logits, temperature)
    validation_predicted = validation_probabilities.argmax(axis=1)
    holdout_predicted = holdout_probabilities.argmax(axis=1)
    threshold_evidence = select_confidence_threshold(validation_probabilities, validation_actual)
    confidence_threshold = float(threshold_evidence["threshold"])
    holdout_accepted = holdout_probabilities.max(axis=1) >= confidence_threshold
    holdout_correct = holdout_predicted == holdout_actual
    validation_labels = np.asarray([classes[index] for index in validation_actual])
    validation_predictions = np.asarray([classes[index] for index in validation_predicted])
    holdout_labels = np.asarray([classes[index] for index in holdout_actual])
    holdout_predictions = np.asarray([classes[index] for index in holdout_predicted])
    metrics = {
        "validation": _classification_metrics(validation_labels, validation_predictions, classes),
        "holdout": _classification_metrics(holdout_labels, holdout_predictions, classes),
        "holdout_loss": holdout_loss,
        "best_validation_macro_f1": best_validation_f1,
        "epochs_completed": len(history),
        "video_group_leakage": False,
        "participant_grouped_holdout": False,
        "validation_scope": "stratified_video_group_train_validation_holdout",
        "deployment_status": "development_candidate",
        "calibration": {
            "method": "temperature_scaling_validation",
            "temperature": temperature,
            "validation_nll_before": negative_log_likelihood(validation_logits, validation_actual),
            "validation_nll_after": negative_log_likelihood(validation_logits, validation_actual, temperature),
            "validation_ece_before": expected_calibration_error(
                calibrated_probabilities(validation_logits), validation_actual
            ),
            "validation_ece_after": expected_calibration_error(validation_probabilities, validation_actual),
            "holdout_nll_before": negative_log_likelihood(holdout_logits, holdout_actual),
            "holdout_nll_after": negative_log_likelihood(holdout_logits, holdout_actual, temperature),
            "holdout_ece_before": expected_calibration_error(
                calibrated_probabilities(holdout_logits), holdout_actual
            ),
            "holdout_ece_after": expected_calibration_error(holdout_probabilities, holdout_actual),
        },
        "abstention": {
            **threshold_evidence,
            "holdout_accepted_count": int(holdout_accepted.sum()),
            "holdout_coverage": float(holdout_accepted.mean()),
            "holdout_selective_accuracy": (
                float(holdout_correct[holdout_accepted].mean()) if holdout_accepted.any() else None
            ),
            "holdout_abstention_rate": float(1.0 - holdout_accepted.mean()),
        },
    }

    model_id = f"exercise_pose_gru_{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')}"
    model_dir = output_dir / model_id
    model_dir.mkdir(parents=True, exist_ok=False)
    model.eval()
    cpu_model = model.cpu()
    example = torch.zeros(1, sequence_length, len(columns), dtype=torch.float32)
    traced = torch.jit.trace(cpu_model, example)
    artifact_path = model_dir / "model.pt"
    traced.save(str(artifact_path))
    metadata = {
        "model_id": model_id,
        "model_name": "bidirectional_gru_attention_pose_classifier",
        "artifact_format": "torchscript_sequence",
        "track": "video_pose_recognition",
        "feature_columns": columns,
        "sequence_length": sequence_length,
        "feature_mean": feature_mean.tolist(),
        "feature_std": feature_std.tolist(),
        "classes": classes,
        "status": "candidate",
        "promoted_to_app": False,
        "requires_manual_confirmation": True,
        "calibration_method": "temperature_scaling_validation",
        "temperature": temperature,
        "confidence_threshold": confidence_threshold,
        "abstention_status": "enabled",
        "participant_grouped_holdout": False,
        "validation_scope": metrics["validation_scope"],
        "artifact_sha256": hashlib.sha256(artifact_path.read_bytes()).hexdigest(),
        "artifact_size_bytes": artifact_path.stat().st_size,
        "architecture": {
            "type": "bidirectional_gru_attention",
            "input_size": len(columns),
            "hidden_size": hidden_size,
            "num_layers": 2,
            "dropout": 0.25,
        },
        "source_features_sha256": hashlib.sha256(features_path.read_bytes()).hexdigest(),
        "training_dependencies": {
            "numpy": np.__version__, "pandas": pd.__version__,
            "scikit_learn": sklearn.__version__, "torch": torch.__version__,
        },
    }
    (model_dir / "metadata.json").write_text(json.dumps(metadata, indent=2), encoding="utf-8")
    (model_dir / "metrics.json").write_text(json.dumps(metrics, indent=2), encoding="utf-8")
    (model_dir / "classification_report.json").write_text(
        json.dumps(metrics["holdout"]["classification_report"], indent=2), encoding="utf-8"
    )
    (model_dir / "training_history.json").write_text(json.dumps(history, indent=2), encoding="utf-8")
    split_rows = []
    for split_name, indexes in split_indexes.items():
        split_rows.extend(
            {"group_id": groups[index], "exercise_id": labels[index], "split": split_name}
            for index in indexes
        )
    pd.DataFrame(split_rows).sort_values(["split", "exercise_id", "group_id"]).to_csv(
        model_dir / "split_manifest.csv", index=False
    )
    (model_dir / "model_card.md").write_text(
        "# Temporal Exercise Classifier — Development Candidate\n\n"
        "This bidirectional GRU uses complete pose sequences resampled to a fixed duration. "
        "Training, validation, and holdout videos are disjoint and stratified by exercise. "
        "Participant identities are unavailable, so unseen-person and clinical performance are not established. "
        "Validation-set temperature scaling calibrates confidence, and an evidence-derived threshold "
        "returns an uncertain result below the accepted range. Predictions above the threshold still "
        "require manual confirmation and do not provide movement-quality feedback.\n",
        encoding="utf-8",
    )
    summary.update({
        "trained": True,
        "model_id": model_id,
        "output_dir": str(model_dir),
        "device": str(device),
        "device_warning": device_warning,
        "metrics": metrics,
    })
    return summary


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--features-path", type=Path, default=DEFAULT_FEATURES)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--epochs", type=int, default=80)
    parser.add_argument("--batch-size", type=int, default=16)
    parser.add_argument("--sequence-length", type=int, default=64)
    parser.add_argument("--hidden-size", type=int, default=64)
    parser.add_argument("--learning-rate", type=float, default=1e-3)
    parser.add_argument("--patience", type=int, default=12)
    parser.add_argument("--device", choices=["auto", "cpu", "cuda"], default="auto")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    result = train_candidate(
        args.features_path,
        args.output_dir,
        epochs=args.epochs,
        batch_size=args.batch_size,
        sequence_length=args.sequence_length,
        hidden_size=args.hidden_size,
        learning_rate=args.learning_rate,
        patience=args.patience,
        device_request=args.device,
        dry_run=args.dry_run,
    )
    print(json.dumps(result, indent=2, default=str))
    return 0 if args.dry_run or result.get("trained") else 2


if __name__ == "__main__":
    raise SystemExit(main())
