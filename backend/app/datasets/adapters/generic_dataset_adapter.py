from __future__ import annotations

from pathlib import Path

from app.datasets.base_adapter import DatasetAdapter


class GenericDatasetAdapter(DatasetAdapter):
    dataset_name = "generic_dataset"
    modality = "unknown"

    def list_samples(self) -> list[Path]:
        if not self.source_path.exists():
            return []
        return sorted(
            item for item in self.source_path.rglob("*")
            if item.is_file() and item.name.lower() != ".gitkeep"
        )

    def normalize_labels(self, raw_label: str) -> tuple[str, str]:
        return "unknown", "unknown"

    def is_compatible_with_current_pipeline(self) -> bool:
        return False

