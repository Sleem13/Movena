from pathlib import Path

import pandas as pd

from scripts.create_manual_annotation_template import ANNOTATION_COLUMNS
from scripts.validate_manual_rep_annotations import validate_annotations


def test_incomplete_annotations_produce_reports_without_failure(tmp_path: Path):
    source = tmp_path / "annotations.csv"
    report = tmp_path / "report.md"
    results = tmp_path / "results.csv"
    row = {column: "" for column in ANNOTATION_COLUMNS}
    row.update({"video_path": "video.mp4", "exercise_label": "squat_correct", "dataset_source": "custom"})
    pd.DataFrame([row]).to_csv(source, index=False)

    summary = validate_annotations(source, report, results)

    assert summary["total_rows"] == 1
    assert summary["complete_rows"] == 0
    assert summary["missing_expected_reps"] == 1
    assert report.exists() and results.exists()
    assert "INCOMPLETE" in report.read_text(encoding="utf-8")
