import pandas as pd

from scripts.export_unified_dataset_metadata import export_unified_metadata


def test_export_uses_specific_adapters_and_limit(tmp_path):
    source = tmp_path / "uci" / "s1" / "e1" / "u1"
    source.mkdir(parents=True)
    (source / "test.txt").write_text("1 2\n", encoding="utf-8")
    (source.parent / "u2").mkdir()
    (source.parent / "u2" / "test.txt").write_text("3 4\n", encoding="utf-8")
    pd.DataFrame([{
        "dataset_name": "uci_physical_therapy_exercises", "source_path": str(tmp_path / "uci"),
        "status": "needs_manual_mapping", "primary_modality": "sensor_timeseries",
        "requires_manual_label_mapping": True,
    }]).to_csv(tmp_path / "registry.csv", index=False)
    result = export_unified_metadata(
        tmp_path / "registry.csv", tmp_path / "samples.csv", tmp_path / "summary.md", limit_per_dataset=1
    )
    assert len(result) == 1
    assert result.iloc[0].adapter_name == "UCIPhysicalTherapyAdapter"
    assert result.iloc[0].label_quality == "low"
    assert bool(result.iloc[0].requires_manual_review)

