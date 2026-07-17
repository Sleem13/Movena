import json

import pytest

from models.dl.train_sequence_model import WARNING, run_synthetic_training


def test_synthetic_sequence_dry_run_resolves_device_without_training(tmp_path):
    pytest.importorskip("torch")
    result = run_synthetic_training(device_request="auto", epochs=1, batch_size=4, output_dir=tmp_path, dry_run=True, samples=12)
    assert result["status"] == "dry_run"
    assert result["warning"] == WARNING
    assert not (tmp_path / "synthetic_sequence_metrics.json").exists()


def test_tiny_synthetic_sequence_training_writes_metrics(tmp_path):
    pytest.importorskip("torch")
    result = run_synthetic_training(
        device_request="cpu", epochs=1, batch_size=4, output_dir=tmp_path,
        samples=18, sequence_length=5, input_size=4, hidden_size=6, classes=3,
    )
    assert result["status"] == "success"
    assert result["promoted_to_app"] is False
    saved = json.loads((tmp_path / "synthetic_sequence_metrics.json").read_text(encoding="utf-8"))
    assert saved["warning"] == WARNING
    assert "not a production model" in (tmp_path / "synthetic_sequence_report.md").read_text(encoding="utf-8")

