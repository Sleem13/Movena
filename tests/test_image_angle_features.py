import csv
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT / "scripts") not in sys.path:
    sys.path.insert(0, str(REPO_ROOT / "scripts"))

from create_image_angle_features import create_angle_features


def write_landmarks(path: Path) -> None:
    points = {
        "left_shoulder": (0.40, 0.20),
        "right_shoulder": (0.60, 0.20),
        "left_hip": (0.42, 0.50),
        "right_hip": (0.58, 0.50),
        "left_knee": (0.42, 0.70),
        "right_knee": (0.58, 0.70),
        "left_ankle": (0.52, 0.85),
        "right_ankle": (0.48, 0.85),
        "left_heel": (0.48, 0.90),
        "right_heel": (0.52, 0.90),
        "left_foot_index": (0.58, 0.90),
        "right_foot_index": (0.42, 0.90),
    }
    fieldnames = [
        "source_dataset",
        "image_path",
        "label",
        "landmark_id",
        "landmark_name",
        "x",
        "y",
        "z",
        "visibility",
    ]
    with path.open("w", newline="", encoding="utf-8") as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
        writer.writeheader()
        for index, (name, (x, y)) in enumerate(points.items()):
            writer.writerow(
                {
                    "source_dataset": "zenodo_squat_dataset",
                    "image_path": "dummy.png",
                    "label": "good",
                    "landmark_id": index,
                    "landmark_name": name,
                    "x": x,
                    "y": y,
                    "z": 0,
                    "visibility": 1,
                }
            )


def test_create_image_angle_features_from_synthetic_landmarks(tmp_path):
    input_path = tmp_path / "landmarks.csv"
    output_path = tmp_path / "features.csv"
    write_landmarks(input_path)

    created = create_angle_features(input_path, output_path)
    with created.open("r", newline="", encoding="utf-8") as csv_file:
        rows = list(csv.DictReader(csv_file))

    assert created == output_path
    assert len(rows) == 1
    assert rows[0]["label"] == "good"
    assert 0 <= float(rows[0]["left_knee_angle"]) <= 180
    assert 0 <= float(rows[0]["trunk_angle"]) <= 180
    assert float(rows[0]["left_heel_foot_vertical_delta"]) == pytest.approx(0.0)


def test_create_image_angle_features_requires_landmark_csv(tmp_path):
    with pytest.raises(FileNotFoundError, match="Image landmark CSV not found"):
        create_angle_features(tmp_path / "missing.csv", tmp_path / "features.csv")
