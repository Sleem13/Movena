from app.datasets.adapters.exercise_pose_frames_adapter import ExercisePoseFramesAdapter


def test_pose_frame_adapter_audits_without_promoting(tmp_path):
    table = tmp_path / "pose.csv"
    table.write_text("workout_type,video_name\nsquat,a.mp4\npush-up,b.mp4\n", encoding="utf-8")
    adapter = ExercisePoseFramesAdapter(table)
    assert adapter.is_available() is True
    assert adapter.normalize_labels("shoulder press") == ("shoulder_press", "unknown")
    assert adapter.infer_exercises() == ["bodyweight_squat", "push_up"]
    assert adapter.load_annotations()["video_count"] == 2
    assert adapter.is_compatible_with_current_pipeline() is False

