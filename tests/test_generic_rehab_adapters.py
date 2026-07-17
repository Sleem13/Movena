from app.datasets.adapters.rehab24_6_adapter import Rehab246Adapter
from app.datasets.adapters.uco_physical_rehab_adapter import UCOPhysicalRehabAdapter
from app.datasets.modality_guard import check_modality_compatibility


def test_rehab24_infers_per_file_modality_without_mapping_ex_code(tmp_path):
    sample = tmp_path / "2d_joints" / "Ex1" / "PM_001-c17.npy"
    sample.parent.mkdir(parents=True)
    sample.write_bytes(b"array")
    row = Rehab246Adapter(tmp_path).export_unified_metadata()[0]
    assert row["modality"] == "skeleton_2d"
    assert row["raw_label"] == "Ex1"
    assert row["exercise_id"] == "unknown"
    assert not check_modality_compatibility("skeleton_2d", "sensor_timeseries_pipeline").allowed


def test_missing_uco_dataset_is_safe(tmp_path):
    adapter = UCOPhysicalRehabAdapter(tmp_path / "missing")
    assert adapter.list_samples() == []
    assert adapter.export_unified_metadata() == []
    assert adapter.audit()["status"] == "missing_or_incomplete"

