import pandas as pd

from scripts.validate_dataset_adapters import validate_adapters


def test_adapter_validation_uses_small_sample_limit(tmp_path):
    source = tmp_path / "custom" / "squat_correct"
    source.mkdir(parents=True)
    for index in range(3):
        (source / f"{index}.mp4").write_bytes(b"video")
    registry = pd.DataFrame([{"dataset_name": "custom_videos", "source_path": str(source.parent)}])
    registry.to_csv(tmp_path / "registry.csv", index=False)
    result = validate_adapters(tmp_path / "registry.csv", tmp_path / "out.csv", tmp_path / "out.md", sample_limit=2)
    assert result.iloc[0].status == "passed"
    assert result.iloc[0].checked_sample_count == 2

