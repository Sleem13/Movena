import pandas as pd

from scripts.train_exercise_recognition_baseline import train_baseline


def test_gpu_availability_does_not_bypass_one_class_recognition_guard(tmp_path):
    features = tmp_path / "features.csv"
    pd.DataFrame([
        {
            "sample_id": f"s{index}", "dataset_name": "custom", "exercise_id": "bodyweight_squat",
            "recognition_track": "video_pose_recognition", "participant_id": f"p{index}",
            "split": "train", "feature_status": "available_features", "feature_a": float(index),
        }
        for index in range(12)
    ]).to_csv(features, index=False)
    result = train_baseline(
        features, "video_pose_recognition", "random_forest", tmp_path / "models",
        dry_run=True, allow_non_grouped=True, min_samples_per_class=10,
    )
    assert result["valid"] is False
    assert result["trained"] is False
    assert any("two known exercise classes" in reason for reason in result["reasons"])
    assert result["automatic_promotion"] is False

