import sys
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from create_manual_annotation_template import ANNOTATION_COLUMNS
from create_participant_grouped_split import create_grouped_split


def test_participant_grouped_split_has_no_participant_leakage(tmp_path):
    annotations = tmp_path / "annotations.csv"
    rows = []
    labels = ["squat_correct", "squat_knee_valgus", "squat_shallow_depth"]
    for index in range(9):
        row = {column: "" for column in ANNOTATION_COLUMNS}
        row.update({
            "video_path": f"data/raw/video_{index}.mp4",
            "participant_id": f"P{index + 1:03d}",
            "session_id": "S01",
            "exercise_label": labels[index % len(labels)],
            "expected_reps": "4",
        })
        rows.append(row)
    pd.DataFrame(rows).to_csv(annotations, index=False)

    result, summary = create_grouped_split(annotations, tmp_path / "split.csv")

    assert summary["participant_leakage"] is False
    assert summary["is_ready"] is True
    assert set(result["split"]) == {"train", "validation", "holdout"}
    assert result.groupby("participant_id")["split"].nunique().max() == 1


def test_incomplete_participants_are_explicitly_unassigned(tmp_path):
    annotations = tmp_path / "annotations.csv"
    row = {column: "" for column in ANNOTATION_COLUMNS}
    row.update({"video_path": "a.mp4", "exercise_label": "squat_correct"})
    pd.DataFrame([row]).to_csv(annotations, index=False)

    result, summary = create_grouped_split(annotations, tmp_path / "split.csv")

    assert result.iloc[0]["split"] == "unassigned"
    assert summary["is_ready"] is False

