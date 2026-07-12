import csv
import json
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "scripts"))

from augment_custom_squat_videos import METADATA_COLUMNS
from prepare_augmented_squat_videos import validate_augmented_metadata


def test_empty_registry_is_created_with_expected_shape(tmp_path):
    metadata = tmp_path / "labels.csv"
    rows, warnings = validate_augmented_metadata(tmp_path / "augmented", metadata)
    with metadata.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        assert reader.fieldnames == METADATA_COLUMNS
        assert list(reader) == []
    assert rows == []
    assert warnings


def test_missing_source_is_flagged_unsafe(tmp_path):
    output_dir = tmp_path / "augmented"
    output_dir.mkdir()
    augmented = output_dir / "clip.mp4"
    augmented.write_bytes(b"dummy")
    metadata = tmp_path / "labels.csv"
    row = {column: "" for column in METADATA_COLUMNS}
    row.update({
        "source_video_path": str(tmp_path / "missing.mp4"),
        "augmented_video_path": str(augmented),
        "original_label": "squat_correct",
        "augmented_label": "squat_correct",
        "augmentation_type": "brightness",
        "augmentation_parameters": json.dumps({"beta": 10}),
        "safe_for_training": "true",
    })
    with metadata.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=METADATA_COLUMNS)
        writer.writeheader()
        writer.writerow(row)

    rows, warnings = validate_augmented_metadata(output_dir, metadata)

    assert rows[0]["safe_for_training"] == "false"
    assert any("Missing source" in warning for warning in warnings)
