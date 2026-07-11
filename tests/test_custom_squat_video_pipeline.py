import csv
import sys
from pathlib import Path

import pytest


REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT / "scripts") not in sys.path:
    sys.path.insert(0, str(REPO_ROOT / "scripts"))

from create_angle_features import create_features_for_file
from prepare_custom_squat_videos import prepare_custom_videos


def test_prepare_custom_videos_writes_metadata_and_report(tmp_path):
    input_dir = tmp_path / "custom_videos"
    correct = input_dir / "squat_correct"
    unlabeled = input_dir / "squat_unlabeled"
    correct.mkdir(parents=True)
    unlabeled.mkdir(parents=True)
    (correct / "correct.mp4").write_bytes(b"dummy video")
    (unlabeled / "review.mov").write_bytes(b"dummy video")
    (correct / "notes.txt").write_text("not a video", encoding="utf-8")

    metadata_path = tmp_path / "labels.csv"
    report_path = tmp_path / "report.md"
    created_metadata, created_report, count = prepare_custom_videos(
        input_dir, metadata_path, report_path
    )

    with created_metadata.open("r", newline="", encoding="utf-8") as csv_file:
        rows = list(csv.DictReader(csv_file))

    assert count == 2
    assert created_report == report_path
    assert {row["label"] for row in rows} == {"squat_correct", "unlabeled"}
    assert sum(row["is_supported_video"] == "false" for row in rows) == 1
    report = report_path.read_text(encoding="utf-8")
    assert "Total videos found: 2" in report
    assert "`squat_fast_uncontrolled`" in report


def test_prepare_custom_videos_fails_when_no_videos_exist(tmp_path):
    with pytest.raises(FileNotFoundError, match="No supported videos"):
        prepare_custom_videos(tmp_path, tmp_path / "labels.csv", tmp_path / "report.md")


def write_landmark_csv(path: Path) -> None:
    points = {
        "left_shoulder": (0.40, 0.20),
        "right_shoulder": (0.60, 0.20),
        "left_hip": (0.42, 0.50),
        "right_hip": (0.58, 0.50),
        "left_knee": (0.42, 0.70),
        "right_knee": (0.58, 0.70),
        "left_ankle": (0.52, 0.85),
        "right_ankle": (0.48, 0.85),
    }
    fieldnames = [
        "source_dataset",
        "video_path",
        "label",
        "frame_index",
        "timestamp_sec",
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
        for landmark_id, (name, (x, y)) in enumerate(points.items()):
            writer.writerow(
                {
                    "source_dataset": "custom_squat_videos",
                    "video_path": "dummy.mp4",
                    "label": "squat_correct",
                    "frame_index": 0,
                    "timestamp_sec": 0,
                    "landmark_id": landmark_id,
                    "landmark_name": name,
                    "x": x,
                    "y": y,
                    "z": 0,
                    "visibility": 1,
                }
            )


def test_create_custom_video_angle_features(tmp_path):
    landmarks_path = tmp_path / "landmarks.csv"
    output_path = tmp_path / "angles.csv"
    write_landmark_csv(landmarks_path)

    created = create_features_for_file(landmarks_path, output_path)
    with created.open("r", newline="", encoding="utf-8") as csv_file:
        rows = list(csv.DictReader(csv_file))

    assert len(rows) == 1
    assert rows[0]["label"] == "squat_correct"
    assert 0 <= float(rows[0]["left_knee_angle"]) <= 180
    assert 0 <= float(rows[0]["trunk_angle"]) <= 180


def test_create_custom_video_angles_requires_landmarks(tmp_path):
    with pytest.raises(FileNotFoundError, match="Custom squat landmark CSV not found"):
        create_features_for_file(tmp_path / "missing.csv", tmp_path / "angles.csv")
