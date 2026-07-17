from app.datasets.adapters.zenodo_squat_adapter import ZenodoSquatAdapter


def test_zenodo_image_folder_label_is_not_auto_approved(tmp_path):
    image = tmp_path / "train" / "Bad Back" / "one.jpg"
    image.parent.mkdir(parents=True)
    image.write_bytes(b"image")
    row = ZenodoSquatAdapter(tmp_path).export_unified_metadata()[0]
    assert row["modality"] == "image"
    assert row["exercise_id"] == "bodyweight_squat"
    assert row["issue_label"] == "bad_back"
    assert row["label_quality"] == "medium"
    assert row["requires_manual_review"] is True

