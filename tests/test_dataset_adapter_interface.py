from app.datasets.adapters.generic_video_adapter import GenericVideoAdapter
from app.datasets.modality_guard import check_modality_compatibility
def test_generic_adapter_normalizes_unknown_labels_safely(tmp_path):
 p=tmp_path/"uncertain"/"clip.mp4";p.parent.mkdir();p.write_bytes(b"x");a=GenericVideoAdapter(tmp_path,dataset_name="demo");row=a.export_unified_metadata()[0]
 assert row["exercise_id"]=="unknown" and row["requires_manual_review"] is True
 assert not check_modality_compatibility("sensor_timeseries","video_pose_pipeline").allowed
