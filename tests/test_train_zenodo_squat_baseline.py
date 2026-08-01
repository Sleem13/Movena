import csv
import sys
from pathlib import Path

import pytest


REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT / "scripts") not in sys.path:
    sys.path.insert(0, str(REPO_ROOT / "scripts"))

from train_zenodo_squat_baseline import train_zenodo_baselines


LABELS = ["good", "bad_back", "bad_heel"]


def write_training_files(root: Path, duplicate_across_splits: bool = False):
    feature_path = root / "features.csv"
    metadata_path = root / "metadata.csv"
    feature_rows = []
    metadata_rows = []
    for split_index, split in enumerate(("train", "test")):
        for label_index, label in enumerate(LABELS):
            for sample_index in range(3):
                image = root / split / label / f"{sample_index}.jpg"
                image.parent.mkdir(parents=True, exist_ok=True)
                payload = f"{split}-{label}-{sample_index}".encode()
                if duplicate_across_splits and split == "test" and label == "good" and sample_index == 0:
                    payload = b"train-good-0"
                image.write_bytes(payload)
                feature_rows.append(
                    {
                        "source_dataset": "zenodo_squat_dataset",
                        "image_path": str(image),
                        "label": label,
                        "left_knee_angle": 70 + label_index * 20 + sample_index,
                        "trunk_angle": 10 + label_index * 15 + sample_index + split_index * 0.1,
                    }
                )
                metadata_rows.append({"image_path": str(image), "label": label})

    with feature_path.open("w", newline="", encoding="utf-8") as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=feature_rows[0])
        writer.writeheader()
        writer.writerows(feature_rows)
    with metadata_path.open("w", newline="", encoding="utf-8") as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=metadata_rows[0])
        writer.writeheader()
        writer.writerows(metadata_rows)
    return feature_path, metadata_path


def test_trains_research_baseline_and_blocks_promotion_without_participants(tmp_path):
    features, metadata = write_training_files(tmp_path)
    model_dir = tmp_path / "model"

    metrics = train_zenodo_baselines(features, metadata, model_dir)

    assert metrics["dataset_rows"] == 18
    assert metrics["development_rows"] == 9
    assert metrics["fit_development_rows"] == 6
    assert metrics["calibration_rows"] == 3
    assert metrics["holdout_rows"] == 9
    assert metrics["candidate_model"] == "logistic_regression"
    assert metrics["selection_policy"] == "uncalibrated_explainable_candidate_retained; holdout_used_only_to_reject_failed_calibration"
    assert metrics["calibration"]["method"] == "temperature_scaling"
    assert metrics["calibration"]["temperature"] > 0
    assert metrics["calibration"]["decision"] in {
        "rejected_holdout_probability_quality_worsened",
        "improved_but_not_promoted_without_participant_grouped_validation",
    }
    assert metrics["calibration"]["source_holdout_probability_quality"]["after"]["multiclass_log_loss"] >= 0
    assert metrics["promotion_status"] == "blocked_missing_participant_grouped_holdout"
    assert metrics["data_leakage_audit"]["cross_split_exact_duplicate_groups"] == 0
    assert metrics["data_leakage_audit"]["participant_grouped_holdout"] is False
    assert (model_dir / "artifacts" / "zenodo_squat_posture_baseline.pkl").exists()
    assert (model_dir / "artifacts" / "zenodo_squat_posture_temperature_scaled_experiment.pkl").exists()
    assert (model_dir / "metrics.json").exists()


def test_rejects_exact_image_duplicates_across_source_splits(tmp_path):
    features, metadata = write_training_files(tmp_path, duplicate_across_splits=True)

    with pytest.raises(ValueError, match="exact image duplicate"):
        train_zenodo_baselines(features, metadata, tmp_path / "model")
