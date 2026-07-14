import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from audit_raw_datasets import audit_raw_datasets


def test_audit_counts_modalities_and_handles_missing_uco(tmp_path):
    raw = tmp_path / "raw"
    (raw / "custom_videos").mkdir(parents=True)
    (raw / "custom_videos" / "a.mp4").write_bytes(b"video")
    (raw / "custom_videos" / "frame.jpg").write_bytes(b"image")
    (raw / "custom_videos" / "labels.csv").write_text("label\n", encoding="utf-8")
    (raw / "custom_videos" / "meta.json").write_text("{}", encoding="utf-8")

    data = audit_raw_datasets(raw, tmp_path / "inventory.csv", tmp_path / "summary.md")

    custom = data[data.dataset_name == "custom_videos"].iloc[0]
    assert custom.video_count == 1
    assert custom.image_count == 1
    assert custom.csv_count == 1
    assert custom.json_count == 1
    assert json.loads(custom.extension_counts)[".mp4"] == 1
    uco = data[data.dataset_name == "uco_physical_rehab"].iloc[0]
    assert uco.likely_status == "missing_or_incomplete"

