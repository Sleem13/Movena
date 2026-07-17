import pandas as pd

from scripts.train_exercise_recognition_baseline import train_baseline


TRACK = "video_pose_recognition"


def test_dry_run_refuses_fewer_than_two_classes(tmp_path):
    pd.DataFrame([
        {"exercise_id": "bodyweight_squat", "recognition_track": TRACK, "feature_status": "available_features", "participant_id": None, "split": "unassigned", "f1": index}
        for index in range(6)
    ]).to_csv(tmp_path / "features.csv", index=False)
    result = train_baseline(tmp_path / "features.csv", TRACK, "random_forest", tmp_path / "models", dry_run=True, allow_non_grouped=True)
    assert result["valid"] is False
    assert any("two known exercise classes" in reason for reason in result["reasons"])


def test_dry_run_validates_small_two_class_fixture(tmp_path):
    rows = []
    for label, offset in [("bodyweight_squat", 0), ("sit_to_stand", 10)]:
        rows.extend({
            "sample_id": f"{label}-{index}", "dataset_name": "synthetic", "exercise_id": label,
            "recognition_track": TRACK, "feature_status": "available_features", "participant_id": None,
            "split": "unassigned", "f1": offset + index, "f2": offset - index,
        } for index in range(5))
    pd.DataFrame(rows).to_csv(tmp_path / "features.csv", index=False)
    result = train_baseline(tmp_path / "features.csv", TRACK, "random_forest", tmp_path / "models", dry_run=True, allow_non_grouped=True)
    assert result["valid"] is True
    assert result["trained"] is False
    assert result["automatic_promotion"] is False

