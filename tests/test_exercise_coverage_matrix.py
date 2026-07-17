import pandas as pd

from scripts.build_exercise_coverage_matrix import build_coverage_matrix


def test_coverage_matrix_counts_samples(tmp_path):
    samples = pd.DataFrame([
        {"exercise_id": "bodyweight_squat", "dataset_name": "custom", "modality": "video", "requires_manual_review": False, "processing_status": "ready", "label_quality": "high"},
        {"exercise_id": "bodyweight_squat", "dataset_name": "custom", "modality": "video", "requires_manual_review": False, "processing_status": "ready", "label_quality": "high"},
    ])
    taxonomy = pd.DataFrame([{"exercise_id": "bodyweight_squat", "supported_in_app": True, "rule_based_analyzer_status": "active"}])
    samples.to_csv(tmp_path / "samples.csv", index=False)
    taxonomy.to_csv(tmp_path / "taxonomy.csv", index=False)
    result = build_coverage_matrix(tmp_path / "samples.csv", tmp_path / "taxonomy.csv", tmp_path / "out.csv", tmp_path / "out.md")
    assert result.iloc[0].sample_count == 2
    assert result.iloc[0].training_ready_count == 2

