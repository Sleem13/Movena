"""Quick synthetic CPU/CUDA training benchmark for the optional DL sandbox."""

from __future__ import annotations

import argparse
import json
import time
from pathlib import Path
from typing import Any


DEFAULT_REPORT_DIR = Path("reports/gpu")


def _mb(value: int | float) -> float:
    return round(float(value) / (1024 * 1024), 2)


def _benchmark_device(torch, device: str, *, steps: int, batch_size: int, input_dim: int, classes: int, hidden_dim: int) -> dict[str, float]:
    torch.manual_seed(42)
    if device == "cuda":
        torch.cuda.manual_seed_all(42)
        torch.cuda.empty_cache()
        torch.cuda.reset_peak_memory_stats()
    model = torch.nn.Sequential(
        torch.nn.Linear(input_dim, hidden_dim), torch.nn.ReLU(), torch.nn.Linear(hidden_dim, classes)
    ).to(device)
    optimizer = torch.optim.Adam(model.parameters(), lr=0.001)
    loss_fn = torch.nn.CrossEntropyLoss()
    inputs = torch.randn(batch_size, input_dim, device=device)
    targets = torch.randint(0, classes, (batch_size,), device=device)

    start = time.perf_counter()
    for _ in range(steps):
        optimizer.zero_grad(set_to_none=True)
        loss = loss_fn(model(inputs), targets)
        loss.backward()
        optimizer.step()
    if device == "cuda":
        torch.cuda.synchronize()
    elapsed = time.perf_counter() - start
    return {"time_sec": round(elapsed, 6), "steps_per_sec": round(steps / elapsed, 3)}


def run_benchmark(
    *,
    steps: int = 50,
    batch_size: int = 64,
    input_dim: int = 128,
    classes: int = 4,
    hidden_dim: int = 128,
    dry_run: bool = False,
    include_gpu: bool = True,
) -> dict[str, Any]:
    config = {
        "steps": steps, "batch_size": batch_size, "input_dim": input_dim,
        "classes": classes, "hidden_dim": hidden_dim,
    }
    if min(steps, batch_size, input_dim, hidden_dim) < 1 or classes < 2:
        return {"status": "invalid_config", "dry_run": dry_run, "config": config, "message": "Positive sizes and at least two classes are required."}
    try:
        import torch
    except ImportError:
        return {"status": "not_available", "dry_run": dry_run, "config": config, "message": "PyTorch is not installed."}

    cuda_available = bool(torch.cuda.is_available() and include_gpu)
    result: dict[str, Any] = {
        "status": "dry_run" if dry_run else "success",
        "dry_run": dry_run,
        "torch_version": torch.__version__,
        "cuda_available": bool(torch.cuda.is_available()),
        "device_name": torch.cuda.get_device_name(0) if torch.cuda.is_available() else "CPU only",
        "config": config,
        "cpu_time_sec": None,
        "gpu_time_sec": None,
        "cpu_steps_per_sec": None,
        "gpu_steps_per_sec": None,
        "gpu_speedup": None,
        "gpu_memory_allocated_mb": 0.0,
        "gpu_memory_reserved_mb": 0.0,
    }
    if dry_run:
        result["would_benchmark"] = ["cpu"] + (["cuda"] if cuda_available else [])
        return result

    cpu = _benchmark_device(torch, "cpu", **config)
    result["cpu_time_sec"] = cpu["time_sec"]
    result["cpu_steps_per_sec"] = cpu["steps_per_sec"]
    if cuda_available:
        gpu = _benchmark_device(torch, "cuda", **config)
        result["gpu_time_sec"] = gpu["time_sec"]
        result["gpu_steps_per_sec"] = gpu["steps_per_sec"]
        result["gpu_speedup"] = round(cpu["time_sec"] / gpu["time_sec"], 3) if gpu["time_sec"] else None
        result["gpu_memory_allocated_mb"] = _mb(torch.cuda.max_memory_allocated(0))
        result["gpu_memory_reserved_mb"] = _mb(torch.cuda.max_memory_reserved(0))
    return result


def save_benchmark_report(report: dict[str, Any], report_dir: Path = DEFAULT_REPORT_DIR) -> tuple[Path, Path]:
    report_dir.mkdir(parents=True, exist_ok=True)
    json_path = report_dir / "gpu_training_benchmark.json"
    markdown_path = report_dir / "gpu_training_benchmark.md"
    json_path.write_text(json.dumps(report, indent=2), encoding="utf-8")
    lines = ["# GPU Training Benchmark", "", "Synthetic infrastructure benchmark only; not a model-quality result.", ""]
    lines.extend(f"- **{key}**: {value}" for key, value in report.items())
    markdown_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return json_path, markdown_path


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--steps", type=int, default=50)
    parser.add_argument("--batch-size", type=int, default=64)
    parser.add_argument("--input-dim", type=int, default=128)
    parser.add_argument("--classes", type=int, default=4)
    parser.add_argument("--hidden-dim", type=int, default=128)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    report = run_benchmark(
        steps=args.steps, batch_size=args.batch_size, input_dim=args.input_dim,
        classes=args.classes, hidden_dim=args.hidden_dim, dry_run=args.dry_run,
    )
    json_path, markdown_path = save_benchmark_report(report)
    print(json.dumps(report, indent=2))
    print(f"JSON report: {json_path}")
    print(f"Markdown report: {markdown_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

