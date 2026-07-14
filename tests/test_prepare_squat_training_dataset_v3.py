import sys
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from prepare_squat_training_dataset_v3 import prepare_candidates


def test_v3_candidates_exclude_incompatible_and_unknown_sources(tmp_path):
    registry = tmp_path / "registry.csv"
    mapping = tmp_path / "mapping.csv"
    labels = tmp_path / "labels.csv"
    annotations = tmp_path / "annotations.csv"
    augmented = tmp_path / "augmented.csv"
    pd.DataFrame([
        {"dataset_name": "custom_videos", "source_path": "data/raw/custom_videos", "status": "compatible_candidate", "data_modality": "video", "usable_for_current_squat_mvp": True},
        {"dataset_name": "uci_physical_therapy_exercises", "source_path": "data/raw/uci", "status": "adapter_required", "data_modality": "sensor_timeseries", "usable_for_current_squat_mvp": False},
    ]).to_csv(registry, index=False)
    pd.DataFrame([
        {"raw_dataset_name": "custom_videos", "raw_label": "squat_correct", "normalized_exercise": "bodyweight_squat", "normalized_issue_label": "squat_correct", "confidence": "high", "notes": ""},
        {"raw_dataset_name": "uci_physical_therapy_exercises", "raw_label": "E1", "normalized_exercise": "unknown", "normalized_issue_label": "unknown", "confidence": "low", "notes": ""},
    ]).to_csv(mapping, index=False)
    pd.DataFrame([
        {"video_path": "data/raw/custom_videos/squat_correct/a.mp4", "label": "squat_correct", "is_supported_video": True},
        {"video_path": "data/raw/custom_videos/unknown/b.mp4", "label": "unknown", "is_supported_video": True},
    ]).to_csv(labels, index=False)
    pd.DataFrame([{"video_path": "data/raw/custom_videos/squat_correct/a.mp4", "participant_id": "P001", "view_type": "side"}]).to_csv(annotations, index=False)
    pd.DataFrame(columns=["safe_for_training", "augmented_label", "augmented_video_path", "source_video_path"]).to_csv(augmented, index=False)

    result = prepare_candidates(registry, mapping, labels, annotations, augmented, tmp_path / "v3.csv", tmp_path / "summary.md")

    assert len(result) == 1
    assert result.iloc[0].dataset_source == "custom_videos"
    assert result.iloc[0].participant_id == "P001"
    assert "uci_physical_therapy_exercises" not in set(result.dataset_source)
