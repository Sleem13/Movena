import sys
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from create_manual_annotation_template import ANNOTATION_COLUMNS
from validate_manual_rep_annotations import validate_annotations


def row(**overrides):
    value = {column: "" for column in ANNOTATION_COLUMNS}
    value.update({
        "video_path": "a.mp4", "participant_id": "P001", "session_id": "S01",
        "exercise_label": "squat_correct", "expected_reps": "4", "view_type": "side",
        "recording_quality": "good", "annotator": "qa", "annotation_confidence": "high",
    })
    value.update(overrides)
    return value


def test_annotation_validation_reports_missing_invalid_and_duplicates(tmp_path):
    annotations = tmp_path / "annotations.csv"
    report = tmp_path / "report.md"
    pd.DataFrame([
        row(),
        row(video_path="a.mp4", participant_id="bad id", expected_reps=""),
        row(video_path="b.mp4", participant_id="P002", expected_reps="3.5"),
    ]).to_csv(annotations, index=False)

    summary = validate_annotations(annotations, report)

    assert summary["is_ready"] is False
    assert summary["missing_expected_reps"] == 1
    assert summary["invalid_expected_reps"] == 1
    assert summary["invalid_participant_ids"] == 1
    assert summary["duplicate_video_rows"] == 2
    assert "squat_fast_uncontrolled" in summary["missing_supported_classes"]
    assert "Status: INCOMPLETE" in report.read_text(encoding="utf-8")
