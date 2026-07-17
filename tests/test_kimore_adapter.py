from app.datasets.adapters.kimore_adapter import KiMoReAdapter


def test_kimore_container_stays_unknown_and_is_not_unpickled(tmp_path):
    (tmp_path / "dataset.pkl").write_bytes(b"not a trusted pickle")
    adapter = KiMoReAdapter(tmp_path)
    row = adapter.export_unified_metadata()[0]
    assert row["exercise_id"] == "unknown"
    assert row["requires_manual_review"] is True
    assert adapter.load_annotations()["status"] == "not_loaded"

