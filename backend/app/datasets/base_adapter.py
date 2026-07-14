"""Base contract for audited dataset-specific adapters."""

from __future__ import annotations

from abc import ABC, abstractmethod
from collections import Counter
from pathlib import Path


class DatasetAdapter(ABC):
    dataset_name = "unknown"
    modality = "unknown"

    def __init__(self, source_path: Path | str):
        self.source_path = Path(source_path)

    def is_available(self) -> bool:
        return self.source_path.is_dir() and any(
            item.is_file() and item.name.lower() != ".gitkeep"
            for item in self.source_path.rglob("*")
        )

    def audit(self) -> dict[str, object]:
        samples = self.list_samples()
        return {
            "dataset_name": self.dataset_name,
            "source_path": str(self.source_path),
            "modality": self.modality,
            "available": self.is_available(),
            "sample_count": len(samples),
            "extension_counts": dict(Counter(path.suffix.lower() for path in samples)),
            "compatible_with_current_pipeline": self.is_compatible_with_current_pipeline(),
        }

    @abstractmethod
    def list_samples(self) -> list[Path]:
        """List candidate sample files without loading them."""

    def extract_metadata(self) -> list[dict[str, object]]:
        return [
            {
                "dataset_name": self.dataset_name,
                "sample_path": str(path),
                "raw_label": path.parent.name,
                "file_extension": path.suffix.lower(),
                "file_size_bytes": path.stat().st_size,
            }
            for path in self.list_samples()
        ]

    @abstractmethod
    def normalize_labels(self, raw_label: str) -> tuple[str, str]:
        """Return normalized exercise and issue labels, or unknown values."""

    @abstractmethod
    def is_compatible_with_current_pipeline(self) -> bool:
        """Return true only for explicitly supported squat-video inputs."""

