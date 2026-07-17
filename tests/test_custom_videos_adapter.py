from app.datasets.adapters.custom_videos_adapter import CustomVideosAdapter


def test_custom_video_reviewed_and_unknown_folders(tmp_path):
    reviewed = tmp_path / "squat_correct" / "a.mp4"
    unknown = tmp_path / "mystery" / "b.mp4"
    reviewed.parent.mkdir(parents=True)
    unknown.parent.mkdir(parents=True)
    reviewed.write_bytes(b"video")
    unknown.write_bytes(b"video")

    rows = CustomVideosAdapter(tmp_path).export_unified_metadata()
    by_name = {row["file_path"].split("\\")[-1]: row for row in rows}
    assert by_name["a.mp4"]["processing_status"] == "ready"
    assert by_name["a.mp4"]["exercise_id"] == "bodyweight_squat"
    assert by_name["b.mp4"]["requires_manual_review"] is True

