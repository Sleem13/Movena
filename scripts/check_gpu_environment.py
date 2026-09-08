"""Inspect the optional PyTorch/CUDA research environment and save reports."""

from __future__ import annotations

import json
import platform
import sys
from pathlib import Path
from typing import Any


DEFAULT_REPORT_DIR = Path("reports/gpu")


def _mb(value: int | float) -> float:
    return round(float(value) / (1024 * 1024), 2)


def collect_gpu_environment() -> dict[str, Any]:
    report: dict[str, Any] = {
        "python_version": platform.python_version(),
        "torch_installed": False,
        "torch_version": None,
        "cuda_available": False,
        "torch_cuda_version": None,
        "cudnn_available": False,
        "cudnn_version": None,
        "gpu_name": None,
        "gpu_count": 0,
        "gpu_total_memory_mb": 0.0,
        "gpu_allocated_memory_mb": 0.0,
        "gpu_reserved_memory_mb": 0.0,
        "device_capability": None,
        "gpu_ready": False,
    }
    try:
        import torch
    except ImportError:
        report["message"] = "PyTorch is not installed. Install it in an optional DL research environment."
        return report

    report.update({
        "torch_installed": True,
        "torch_version": torch.__version__,
        "cuda_available": bool(torch.cuda.is_available()),
        "torch_cuda_version": torch.version.cuda,
        "cudnn_available": bool(torch.backends.cudnn.is_available()),
        "cudnn_version": torch.backends.cudnn.version() if torch.backends.cudnn.is_available() else None,
        "gpu_count": int(torch.cuda.device_count()) if torch.cuda.is_available() else 0,
    })
    if torch.cuda.is_available() and torch.cuda.device_count() > 0:
        properties = torch.cuda.get_device_properties(0)
        report.update({
            "gpu_name": torch.cuda.get_device_name(0),
            "gpu_total_memory_mb": _mb(properties.total_memory),
            "gpu_allocated_memory_mb": _mb(torch.cuda.memory_allocated(0)),
            "gpu_reserved_memory_mb": _mb(torch.cuda.memory_reserved(0)),
            "device_capability": list(torch.cuda.get_device_capability(0)),
            "gpu_ready": True,
        })
    else:
        report["message"] = "CUDA is unavailable. CPU-safe sandbox commands remain supported."
    return report


def save_gpu_environment_report(report: dict[str, Any], report_dir: Path = DEFAULT_REPORT_DIR) -> tuple[Path, Path]:
    report_dir.mkdir(parents=True, exist_ok=True)
    json_path = report_dir / "gpu_environment_report.json"
    markdown_path = report_dir / "gpu_environment_report.md"
    json_path.write_text(json.dumps(report, indent=2), encoding="utf-8")
    lines = ["# GPU Environment Report", "", "Experimental infrastructure report; not a model-readiness decision.", ""]
    lines.extend(f"- **{key}**: {value}" for key, value in report.items())
    markdown_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return json_path, markdown_path


def main() -> int:
    report = collect_gpu_environment()
    json_path, markdown_path = save_gpu_environment_report(report)
    print("Movena GPU environment")
    print(json.dumps(report, indent=2))
    print(f"JSON report: {json_path}")
    print(f"Markdown report: {markdown_path}")
    if not report["torch_installed"]:
        print("PyTorch is optional and was not found; exiting cleanly.")
    elif not report["cuda_available"]:
        print("CUDA is unavailable; gpu_ready=false and CPU workflows remain available.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

