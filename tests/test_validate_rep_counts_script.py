import csv
from pathlib import Path

from scripts.validate_rep_counts import create_manual_template, run_validation


def write_csv(path: Path, fields: list[str], rows: list[dict[str, object]]):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def test_manual_rep_count_template_is_created_from_metadata(tmp_path):
    metadata = tmp_path / "labels.csv"
    manual = tmp_path / "manual.csv"
    write_csv(
        metadata,
        ["video_path", "label"],
        [
            {"video_path": "data/a.mp4", "label": "squat_correct"},
            {"video_path": "data/b.mp4", "label": "squat_shallow_depth"},
        ],
    )
    assert create_manual_template(metadata, manual) == 2
    rows = list(csv.DictReader(manual.open(encoding="utf-8")))
    assert rows[0] == {"video_path": "data/a.mp4", "expected_reps": "", "notes": ""}


def test_validation_outputs_expected_shape_and_summary(tmp_path):
    manual = tmp_path / "manual.csv"
    output = tmp_path / "reports"
    write_csv(
        manual,
        ["video_path", "expected_reps", "notes"],
        [{"video_path": "data/a.mp4", "expected_reps": 5, "notes": "manual"}],
    )

    def fake_analyze(_path):
        return {
            "predicted_reps": 4,
            "rep_count_confidence": 0.8,
            "ignored_partial_reps": 1,
            "status": "success",
        }

    results, summary, measured = run_validation(manual, output, fake_analyze)
    assert measured == 1
    row = next(csv.DictReader(results.open(encoding="utf-8")))
    assert row["absolute_error"] == "1"
    assert "Mean absolute error: 1.000" in summary.read_text(encoding="utf-8")
    assert "Videos within ±1 rep: 1/1" in summary.read_text(encoding="utf-8")
