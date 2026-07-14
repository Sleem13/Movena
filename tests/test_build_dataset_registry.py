import sys
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from build_dataset_registry import build_registry


def test_registry_separates_video_and_sensor_sources(tmp_path):
    inventory = tmp_path / "inventory.csv"
    base = {"image_count": 0, "csv_count": 0, "json_count": 0, "npy_count": 0, "mat_count": 0, "annotation_candidate_files": "[]", "notes": ""}
    pd.DataFrame([
        {**base, "dataset_name": "custom_videos", "dataset_path": "data/raw/custom_videos", "likely_status": "potentially_compatible", "likely_modality": "video", "total_file_count": 2, "video_count": 2},
        {**base, "dataset_name": "uci_physical_therapy_exercises", "dataset_path": "data/raw/uci", "likely_status": "adapter_required", "likely_modality": "sensor_timeseries", "total_file_count": 3, "video_count": 0},
    ]).to_csv(inventory, index=False)

    result = build_registry(inventory, tmp_path / "registry.csv", tmp_path / "summary.md")

    custom = result[result.dataset_name == "custom_videos"].iloc[0]
    sensor = result[result.dataset_name == "uci_physical_therapy_exercises"].iloc[0]
    assert bool(custom.usable_for_current_squat_mvp) is True
    assert bool(sensor.requires_adapter) is True
    assert bool(sensor.usable_for_current_squat_mvp) is False

