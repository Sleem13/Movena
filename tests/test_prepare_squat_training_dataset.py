import sys
from pathlib import Path

import pandas as pd


REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "scripts"))

from prepare_squat_training_dataset import feature_columns, prepare_training_dataset


def test_video_angle_aggregation_and_curated_join(tmp_path):
    angles = pd.DataFrame([
        {"source_dataset": "custom_squat_videos", "video_path": "data\\raw\\a.mp4", "left_knee_angle": 100, "right_knee_angle": 110, "left_hip_angle": 80, "right_hip_angle": 84, "trunk_angle": 10},
        {"source_dataset": "custom_squat_videos", "video_path": "data\\raw\\a.mp4", "left_knee_angle": 120, "right_knee_angle": 130, "left_hip_angle": 90, "right_hip_angle": 94, "trunk_angle": 30},
        {"source_dataset": "custom_squat_videos", "video_path": "data/raw/b.mp4", "left_knee_angle": 150, "right_knee_angle": 150, "left_hip_angle": 120, "right_hip_angle": 120, "trunk_angle": 5},
    ])
    labels = pd.DataFrame([
        {"video_path": "data/raw/a.mp4", "label": "squat_correct", "is_supported_video": True},
        {"video_path": "data/raw/b.mp4", "label": "unlabeled", "is_supported_video": True},
    ])
    split = pd.DataFrame([
        {"video_path": "data/raw/a.mp4", "label": "squat_shallow_depth", "split": "validation"},
        {"video_path": "data/raw/b.mp4", "label": "unlabeled", "split": "validation"},
    ])
    angles_path, labels_path, split_path = tmp_path / "angles.csv", tmp_path / "labels.csv", tmp_path / "split.csv"
    angles.to_csv(angles_path, index=False)
    labels.to_csv(labels_path, index=False)
    split.to_csv(split_path, index=False)

    result = prepare_training_dataset(angles_path, labels_path, split_path, tmp_path / "features.csv")

    assert len(result) == 1
    assert result.iloc[0]["label"] == "squat_shallow_depth"
    assert result.iloc[0]["left_knee_angle_mean"] == 110
    assert result.iloc[0]["left_knee_angle_range"] == 20
    assert result.iloc[0]["knee_angle_asymmetry"] == 10
    assert result.iloc[0]["estimated_depth_proxy"] == 80
    assert set(feature_columns()).issubset(result.columns)
