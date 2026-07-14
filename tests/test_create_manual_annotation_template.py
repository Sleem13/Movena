import sys
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from create_manual_annotation_template import ANNOTATION_COLUMNS, create_annotation_template


def test_template_creation_preserves_existing_annotations(tmp_path):
    labels = tmp_path / "labels.csv"
    augmented = tmp_path / "augmented.csv"
    output = tmp_path / "annotations.csv"
    pd.DataFrame([
        {"video_path": "data\\raw\\a.mp4", "label": "squat_correct", "is_supported_video": True},
        {"video_path": "data/raw/skip.txt", "label": "unlabeled", "is_supported_video": False},
    ]).to_csv(labels, index=False)
    pd.DataFrame([{
        "augmented_video_path": "data/augmented/a_bright.mp4",
        "augmented_label": "squat_correct",
        "safe_for_training": True,
    }]).to_csv(augmented, index=False)
    pd.DataFrame([{
        **{column: "" for column in ANNOTATION_COLUMNS},
        "video_path": "data/raw/a.mp4",
        "participant_id": "P001",
        "expected_reps": "4",
        "annotator": "reviewer-a",
    }]).to_csv(output, index=False)

    result, added, preserved = create_annotation_template(labels, augmented, output)

    assert len(result) == 2
    assert added == 1
    assert preserved == 1
    real = result[result["video_path"] == "data/raw/a.mp4"].iloc[0]
    assert real["participant_id"] == "P001"
    assert str(real["expected_reps"]) == "4"
    assert real["exercise_label"] == "squat_correct"

