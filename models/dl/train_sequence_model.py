"""CPU/CUDA-safe synthetic sequence-classification sandbox."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

import numpy as np


ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from models.dl.lstm_classifier import LSTMClassifier


WARNING = "This is an experimental synthetic DL sandbox. It is not a production model."
DEFAULT_OUTPUT_DIR = Path("models/dl_experiments")


def resolve_device(requested: str, torch_module=None) -> tuple[str, str | None]:
    if requested not in {"auto", "cpu", "cuda"}:
        raise ValueError("device must be auto, cpu, or cuda")
    if torch_module is None:
        try:
            import torch as torch_module
        except ImportError:
            return "cpu", "PyTorch is not installed; training is unavailable."
    available = bool(torch_module.cuda.is_available())
    if requested == "auto":
        return ("cuda" if available else "cpu"), None
    if requested == "cuda" and not available:
        return "cpu", "CUDA was requested but is unavailable; falling back to CPU."
    return requested, None


def _synthetic_sequences(samples: int, sequence_length: int, input_size: int, classes: int, seed: int = 42):
    rng = np.random.default_rng(seed)
    labels = np.arange(samples, dtype=np.int64) % classes
    sequences = rng.normal(0, 0.35, size=(samples, sequence_length, input_size)).astype(np.float32)
    time_axis = np.linspace(0, 2 * np.pi, sequence_length, dtype=np.float32)
    for index, label in enumerate(labels):
        sequences[index, :, label % input_size] += np.sin(time_axis * (label + 1)) + label * 0.5
    order = rng.permutation(samples)
    return sequences[order], labels[order]


def run_synthetic_training(
    *,
    device_request: str = "auto",
    epochs: int = 2,
    batch_size: int = 16,
    output_dir: Path = DEFAULT_OUTPUT_DIR,
    dry_run: bool = False,
    samples: int = 96,
    sequence_length: int = 12,
    input_size: int = 8,
    hidden_size: int = 24,
    classes: int = 3,
) -> dict[str, Any]:
    try:
        import torch
        from torch.utils.data import DataLoader, TensorDataset
    except ImportError:
        return {"status": "not_available", "experimental": True, "warning": WARNING, "message": "PyTorch is not installed."}

    device, device_warning = resolve_device(device_request, torch)
    config = {
        "device_requested": device_request, "device_resolved": device, "epochs": epochs,
        "batch_size": batch_size, "samples": samples, "sequence_length": sequence_length,
        "input_size": input_size, "hidden_size": hidden_size, "classes": classes,
    }
    if min(epochs, batch_size, samples, sequence_length, input_size, hidden_size) < 1 or classes < 2:
        return {"status": "invalid_config", "experimental": True, "warning": WARNING, "config": config}
    if dry_run:
        return {"status": "dry_run", "experimental": True, "warning": WARNING, "config": config, "device_warning": device_warning}

    torch.manual_seed(42)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(42)
    sequences, labels = _synthetic_sequences(samples, sequence_length, input_size, classes)
    split = max(classes, int(samples * 0.8))
    split = min(split, samples - classes)
    train_data = TensorDataset(torch.from_numpy(sequences[:split]), torch.from_numpy(labels[:split]))
    test_data = TensorDataset(torch.from_numpy(sequences[split:]), torch.from_numpy(labels[split:]))
    generator = torch.Generator().manual_seed(42)
    train_loader = DataLoader(train_data, batch_size=batch_size, shuffle=True, num_workers=0, generator=generator)
    test_loader = DataLoader(test_data, batch_size=batch_size, shuffle=False, num_workers=0)

    model = LSTMClassifier(input_size=input_size, hidden_size=hidden_size, num_classes=classes).to(device)
    optimizer = torch.optim.Adam(model.parameters(), lr=0.001)
    loss_fn = torch.nn.CrossEntropyLoss()
    epoch_losses: list[float] = []
    model.train()
    for _ in range(epochs):
        total_loss = 0.0
        batches = 0
        for inputs, targets in train_loader:
            inputs, targets = inputs.to(device), targets.to(device)
            optimizer.zero_grad(set_to_none=True)
            loss = loss_fn(model(inputs), targets)
            loss.backward()
            optimizer.step()
            total_loss += float(loss.detach().cpu())
            batches += 1
        epoch_losses.append(round(total_loss / max(batches, 1), 6))

    model.eval()
    correct = total = 0
    with torch.no_grad():
        for inputs, targets in test_loader:
            predictions = model(inputs.to(device)).argmax(dim=1).cpu()
            correct += int((predictions == targets).sum())
            total += len(targets)
    metrics = {
        "status": "success", "experimental": True, "warning": WARNING,
        "device": device, "device_name": torch.cuda.get_device_name(0) if device == "cuda" else "CPU",
        "epochs": epochs, "batch_size": batch_size, "train_samples": len(train_data),
        "test_samples": len(test_data), "classes": classes, "epoch_losses": epoch_losses,
        "test_accuracy": round(correct / max(total, 1), 6), "promoted_to_app": False,
        "device_warning": device_warning,
    }
    output_dir.mkdir(parents=True, exist_ok=True)
    metrics_path = output_dir / "synthetic_sequence_metrics.json"
    report_path = output_dir / "synthetic_sequence_report.md"
    metrics_path.write_text(json.dumps(metrics, indent=2), encoding="utf-8")
    report_path.write_text(
        "# Synthetic Sequence DL Sandbox\n\n"
        f"**{WARNING}**\n\n"
        f"- Device: {metrics['device']} ({metrics['device_name']})\n"
        f"- Epochs: {epochs}\n- Train/test samples: {len(train_data)}/{len(test_data)}\n"
        f"- Test accuracy: {metrics['test_accuracy']}\n- Promoted to app: false\n\n"
        "Synthetic accuracy is a software smoke test, not evidence of real movement-recognition performance.\n",
        encoding="utf-8",
    )
    return metrics


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--synthetic", action="store_true")
    parser.add_argument("--device", choices=["auto", "cpu", "cuda"], default="auto")
    parser.add_argument("--epochs", type=int, default=2)
    parser.add_argument("--batch-size", type=int, default=16)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    parser.add_argument("--features-path", type=Path)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    print(WARNING)
    if not args.synthetic:
        print("No implicit real-data training is permitted. Pass --synthetic for the sandbox.")
        if args.features_path:
            print(f"Feature input was provided but real sequence training remains gated: {args.features_path}")
        return 0
    result = run_synthetic_training(
        device_request=args.device, epochs=args.epochs, batch_size=args.batch_size,
        output_dir=args.output_dir, dry_run=args.dry_run,
    )
    print(json.dumps(result, indent=2))
    return 0 if result.get("status") in {"success", "dry_run"} else 2


if __name__ == "__main__":
    raise SystemExit(main())
