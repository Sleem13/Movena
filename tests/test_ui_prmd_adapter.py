from app.datasets.adapters.ui_prmd_adapter import UIPRMDAdapter


def test_ui_prmd_separates_annotation_file_from_samples(tmp_path):
    (tmp_path / "input.csv").write_text("x\n1\n", encoding="utf-8")
    (tmp_path / "label.csv").write_text("label\ne1\n", encoding="utf-8")
    adapter = UIPRMDAdapter(tmp_path)
    assert [path.name for path in adapter.list_samples()] == ["input.csv"]
    assert adapter.load_annotations()["available"] is True
    assert adapter.export_unified_metadata()[0]["requires_manual_review"] is True

