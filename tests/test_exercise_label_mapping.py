import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from create_exercise_label_mapping import create_mapping, infer_mapping


def test_mapping_keeps_uncertain_labels_unknown(tmp_path):
    raw = tmp_path / "raw"
    (raw / "custom_videos" / "squat_correct").mkdir(parents=True)
    (raw / "mystery" / "ambiguous_class_7").mkdir(parents=True)
    data = create_mapping(raw, tmp_path / "mapping.csv")

    exact = data[(data.raw_dataset_name == "custom_videos") & (data.raw_label == "squat_correct")].iloc[0]
    uncertain = data[(data.raw_dataset_name == "mystery") & (data.raw_label == "ambiguous_class_7")].iloc[0]
    assert exact.normalized_issue_label == "squat_correct"
    assert uncertain.normalized_exercise == "unknown"
    assert uncertain.normalized_issue_label == "unknown"
    assert infer_mapping("zenodo_squat_dataset", "bad_back")["normalized_issue_label"] == "unknown"

