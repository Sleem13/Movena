import csv

from scripts.prepare_knee_extension_training_candidates import OUTPUT_COLUMNS, prepare_candidates


def test_candidate_registry_preserves_source_and_requires_review(tmp_path):
    source = tmp_path / "unified.csv"
    with source.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=["sample_id", "dataset_name", "file_path", "modality", "exercise_id", "raw_label", "normalized_label", "participant_id", "session_id", "view_type", "recording_quality"])
        writer.writeheader()
        writer.writerow({"sample_id": "one", "dataset_name": "example", "file_path": "p/knee_extension/a.mp4", "modality": "video", "exercise_id": "", "raw_label": "knee extension", "normalized_label": "", "participant_id": "p1", "session_id": "s1", "view_type": "side", "recording_quality": "good"})
        writer.writerow({"sample_id": "two", "dataset_name": "example", "file_path": "p/walk/a.mp4", "modality": "video", "exercise_id": "walking_gait_screen", "raw_label": "walk", "normalized_label": "gait", "participant_id": "p2", "session_id": "s2", "view_type": "side", "recording_quality": "good"})
    output = tmp_path / "candidates.csv"
    rows = prepare_candidates(source, output)
    assert len(rows) == 1
    assert rows[0]["requires_manual_review"] == "true"
    assert rows[0]["training_ready"] == "false"
    assert list(csv.DictReader(output.open(encoding="utf-8")))[0]["sample_id"] == "one"
    assert list(csv.DictReader(output.open(encoding="utf-8")))[0].keys() == set(OUTPUT_COLUMNS)
