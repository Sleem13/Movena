import pandas as pd

from scripts.train_exercise_pose_xgboost import validate_features


def test_xgboost_validation_requires_40_features_and_video_groups():
    rows = []
    for exercise in ("bodyweight_squat", "push_up"):
        for video in range(5):
            rows.append({
                "exercise_id": exercise, "group_id": f"{exercise}-{video}",
                "feature_status": "available_features", **{f"f{index}": float(index) for index in range(40)},
            })
    result = validate_features(pd.DataFrame(rows))
    assert result["valid"] is True
    assert result["participant_grouped_holdout"] is False
    assert result["promotion_allowed"] is False

