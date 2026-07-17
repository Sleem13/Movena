from scripts.create_exercise_label_mapping import REQUIRED_MAPPING_COLUMNS, create_mapping


def test_label_mapping_review_columns_and_pending_unknown(tmp_path):
    raw = tmp_path / "raw"
    (raw / "custom_videos" / "squat_correct").mkdir(parents=True)
    (raw / "kimore" / "E1").mkdir(parents=True)
    result = create_mapping(raw, tmp_path / "mapping.csv")
    assert set(REQUIRED_MAPPING_COLUMNS) <= set(result.columns)
    unknown = result[(result.dataset_name == "kimore") & (result.raw_label == "E1")].iloc[0]
    assert bool(unknown.requires_review)
    assert unknown.review_status == "needs_more_info"

