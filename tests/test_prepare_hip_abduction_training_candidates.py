import csv

from scripts.prepare_hip_abduction_training_candidates import prepare_candidates


def test_candidates_preserve_source_and_require_review(tmp_path):
    source = tmp_path / "unified.csv"
    fields = ["sample_id", "dataset_name", "file_path", "modality", "exercise_id", "raw_label", "normalized_label", "participant_id", "session_id", "view_type", "recording_quality"]
    with source.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields); writer.writeheader()
        writer.writerow({"sample_id": "one", "dataset_name": "example", "file_path": "p/hip_abduction/a.mp4", "modality": "video", "exercise_id": "", "raw_label": "standing hip abduction", "normalized_label": "", "participant_id": "p1", "session_id": "s1", "view_type": "front", "recording_quality": "good"})
    rows = prepare_candidates(source, tmp_path / "out.csv")
    assert len(rows) == 1
    assert rows[0]["dataset_name"] == "example" and rows[0]["raw_label"] == "standing hip abduction"
    assert rows[0]["requires_manual_review"] == "true" and rows[0]["training_ready"] == "false"
