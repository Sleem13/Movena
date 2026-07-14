from pathlib import Path

import pandas as pd

from scripts.evaluate_rep_count_accuracy import evaluate_rep_counts


def test_rep_evaluation_skips_blank_counts_and_missing_videos(tmp_path: Path):
    annotations = tmp_path / "annotations.csv"
    existing = tmp_path / "existing.mp4"
    existing.write_bytes(b"fixture")
    pd.DataFrame([
        {"video_path": "existing.mp4", "expected_reps": "3"},
        {"video_path": "blank.mp4", "expected_reps": ""},
        {"video_path": "missing.mp4", "expected_reps": "2"},
    ]).to_csv(annotations, index=False)

    result, summary = evaluate_rep_counts(
        annotations, tmp_path / "results.csv", tmp_path / "summary.md",
        analyze=lambda _path: {
            "predicted_reps": 3, "rep_count_confidence": 0.9,
            "ignored_partial_reps": 0, "analysis_status": "success",
            "validation_warnings": "",
        },
        repo_root=tmp_path,
    )

    assert len(result) == 2
    assert summary["total_annotated_videos"] == 2
    assert summary["evaluated_videos"] == 1
    assert summary["exact_match_rate"] == 1.0
    assert "skipped_missing_video" in set(result["analysis_status"])


def test_rep_evaluation_with_no_completed_annotations_is_valid(tmp_path: Path):
    annotations = tmp_path / "annotations.csv"
    pd.DataFrame([{"video_path": "a.mp4", "expected_reps": ""}]).to_csv(annotations, index=False)

    result, summary = evaluate_rep_counts(
        annotations, tmp_path / "results.csv", tmp_path / "summary.md", repo_root=tmp_path
    )

    assert result.empty
    assert summary["evaluated_videos"] == 0
    assert "No completed" in (tmp_path / "summary.md").read_text(encoding="utf-8")
