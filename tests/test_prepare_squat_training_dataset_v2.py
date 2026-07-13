import json
import sys
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from prepare_squat_training_dataset_v2 import prepare_training_dataset_v2


def angle_row(path, base, source="custom_squat_videos"):
    return {
        "video_path": path, "source_dataset": source,
        "left_knee_angle": base, "right_knee_angle": base + 2,
        "left_hip_angle": base + 10, "right_hip_angle": base + 12,
        "trunk_angle": base / 10,
    }


def test_v2_preserves_real_and_augmented_lineage(tmp_path):
    real_angles = tmp_path / "real_angles.csv"
    real_labels = tmp_path / "real_labels.csv"
    splits = tmp_path / "splits.csv"
    aug_angles = tmp_path / "aug_angles.csv"
    aug_labels = tmp_path / "aug_labels.csv"
    manual_reps = tmp_path / "manual_reps.csv"
    pd.DataFrame([angle_row("data/raw/a.mp4", 100), angle_row("data/raw/new.mp4", 120)]).to_csv(real_angles, index=False)
    pd.DataFrame([
        {"video_path": "data/raw/a.mp4", "label": "squat_correct", "source_dataset": "custom_squat_videos", "is_supported_video": True},
        {"video_path": "data/raw/new.mp4", "label": "squat_knee_valgus", "source_dataset": "custom_squat_videos", "is_supported_video": True},
    ]).to_csv(real_labels, index=False)
    pd.DataFrame([{"video_path": "data/raw/a.mp4", "split": "validation"}]).to_csv(splits, index=False)
    pd.DataFrame([angle_row("data/augmented/a__brightness.mp4", 102, "augmented_custom_squat_videos")]).to_csv(aug_angles, index=False)
    pd.DataFrame([{
        "source_video_path": "data/raw/a.mp4",
        "augmented_video_path": "data/augmented/a__brightness.mp4",
        "original_label": "squat_correct", "augmented_label": "squat_correct",
        "safe_for_training": True, "augmentation_parameters": json.dumps({"beta": 10}),
    }]).to_csv(aug_labels, index=False)
    pd.DataFrame([
        {"video_path": "data/raw/a.mp4", "expected_reps": 4, "notes": "reviewed"},
        {"video_path": "data/raw/new.mp4", "expected_reps": "", "notes": "pending"},
    ]).to_csv(manual_reps, index=False)

    result = prepare_training_dataset_v2(
        real_angles, real_labels, splits, tmp_path / "v2.csv", True, aug_angles, aug_labels,
        manual_reps,
    )

    assert len(result) == 3
    assert set(result["source_type"]) == {"real", "augmented"}
    augmented = result[result["source_type"] == "augmented"].iloc[0]
    assert augmented["original_label"] == "squat_correct"
    assert augmented["augmented_label"] == "squat_correct"
    assert augmented["split"] == "validation"
    assert augmented["manual_expected_reps"] == 4
    assert bool(augmented["manual_rep_count_validated"]) is True
    new_real = result[result["video_path"] == "data/raw/new.mp4"].iloc[0]
    assert new_real["split"] == "development_unassigned"
    assert bool(new_real["manual_rep_count_validated"]) is False
