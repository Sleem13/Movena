import pandas as pd

from scripts.prepare_exercise_pose_recognition_features import build_features


def test_prepare_pose_features_preserves_video_groups(tmp_path):
    row = {"workout_type": "squat", "video_name": "clip-1.mp4"}
    for index in range(17):
        row[f"joint_{index}_x"] = float(index)
        row[f"joint_{index}_y"] = float(index % 3)
        row[f"joint_{index}_conf"] = 1.0
    row.update({
        "joint_5_x": 0.0, "joint_5_y": 1.0, "joint_6_x": 1.0, "joint_6_y": 1.0,
        "joint_11_x": 0.0, "joint_11_y": 0.0, "joint_12_x": 1.0, "joint_12_y": 0.0,
    })
    source = tmp_path / "pose.csv"
    pd.DataFrame([row]).to_csv(source, index=False)
    features, summary = build_features(source)
    assert summary["feature_rows"] == 1
    assert summary["feature_count"] == 40
    assert summary["participant_ids_available"] is False
    assert features.iloc[0].exercise_id == "bodyweight_squat"
    assert features.iloc[0].group_id == "clip-1.mp4"

