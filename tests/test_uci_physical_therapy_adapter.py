from app.datasets.adapters.uci_physical_therapy_adapter import UCIPhysicalTherapyAdapter


def test_uci_adapter_preserves_codes_and_routes_sensor_data(tmp_path):
    sample = tmp_path / "s2" / "e4" / "u3" / "test.txt"
    sample.parent.mkdir(parents=True)
    sample.write_text("0 1 2\n", encoding="utf-8")
    adapter = UCIPhysicalTherapyAdapter(tmp_path)
    row = adapter.export_unified_metadata()[0]
    assert row["raw_label"] == "e4"
    assert row["participant_id"] == "s2"
    assert row["exercise_id"] == "unknown"
    assert adapter.is_compatible_with_pipeline("sensor_timeseries_pipeline")
    assert not adapter.is_compatible_with_pipeline("video_pose_pipeline")

