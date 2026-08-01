import csv
import sys
from pathlib import Path

import pytest

Image = pytest.importorskip("PIL.Image")

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT / "scripts") not in sys.path:
    sys.path.insert(0, str(REPO_ROOT / "scripts"))

from prepare_zenodo_squat_dataset import prepare_dataset


def test_prepare_dataset_creates_normalized_metadata_from_dummy_images(tmp_path):
    input_dir = tmp_path / "raw"
    good_dir = input_dir / "Good"
    bad_back_dir = input_dir / "Bad Back"
    good_dir.mkdir(parents=True)
    bad_back_dir.mkdir(parents=True)

    image = Image.new("RGB", (32, 24), color=(0, 0, 0))
    image.save(good_dir / "good.png")
    image.save(bad_back_dir / "back.jpg")

    output_path = tmp_path / "labels.csv"
    created = prepare_dataset(input_dir, output_path)

    with created.open("r", newline="", encoding="utf-8") as csv_file:
        rows = list(csv.DictReader(csv_file))

    assert created == output_path
    assert {row["label"] for row in rows} == {"good", "bad_back"}
    assert {row["original_label"] for row in rows} == {"Good", "Bad Back"}
    assert {row["source_split"] for row in rows} == {"unknown"}
    assert all(len(row["content_sha256"]) == 64 for row in rows)
    assert all(row["image_width"] == "32" for row in rows)
    assert all(row["image_height"] == "24" for row in rows)
    assert all(int(row["file_size_bytes"]) > 0 for row in rows)


def test_prepare_dataset_fails_helpfully_when_folder_is_empty(tmp_path):
    with pytest.raises(FileNotFoundError, match="No supported images"):
        prepare_dataset(tmp_path, tmp_path / "labels.csv")
