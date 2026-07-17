import json

from scripts.check_gpu_environment import collect_gpu_environment, save_gpu_environment_report


def test_gpu_environment_report_is_cpu_and_cuda_safe(tmp_path):
    report = collect_gpu_environment()
    required = {
        "python_version", "torch_installed", "torch_version", "cuda_available", "torch_cuda_version",
        "cudnn_available", "cudnn_version", "gpu_name", "gpu_count", "gpu_total_memory_mb",
        "gpu_allocated_memory_mb", "gpu_reserved_memory_mb", "device_capability", "gpu_ready",
    }
    assert required <= report.keys()
    json_path, markdown_path = save_gpu_environment_report(report, tmp_path)
    assert json.loads(json_path.read_text(encoding="utf-8"))["gpu_ready"] == report["gpu_ready"]
    assert "GPU Environment Report" in markdown_path.read_text(encoding="utf-8")

