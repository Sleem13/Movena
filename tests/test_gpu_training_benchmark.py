import json

import pytest

from scripts.benchmark_gpu_training import run_benchmark, save_benchmark_report


def test_benchmark_dry_run_is_safe_without_cuda(tmp_path):
    report = run_benchmark(steps=2, batch_size=4, input_dim=8, classes=2, hidden_dim=8, dry_run=True)
    assert report["status"] in {"dry_run", "not_available"}
    json_path, markdown_path = save_benchmark_report(report, tmp_path)
    assert json.loads(json_path.read_text(encoding="utf-8"))["dry_run"] is True
    assert "Synthetic infrastructure benchmark" in markdown_path.read_text(encoding="utf-8")


def test_tiny_cpu_benchmark_runs_when_torch_is_available():
    pytest.importorskip("torch")
    report = run_benchmark(steps=2, batch_size=4, input_dim=8, classes=2, hidden_dim=8, include_gpu=False)
    assert report["status"] == "success"
    assert report["cpu_time_sec"] > 0
    assert report["cpu_steps_per_sec"] > 0

