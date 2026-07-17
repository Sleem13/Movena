from __future__ import annotations

from pathlib import Path

from app.datasets.base_adapter import DatasetAdapter


class GenericDatasetAdapter(DatasetAdapter):
    dataset_name = "generic_dataset"
    modality = "unknown"

    def __init__(self, source_path, dataset_name=None, modality=None):
        super().__init__(source_path)
        if dataset_name: self.dataset_name = dataset_name
        if modality: self.modality = modality

    def list_samples(self, limit: int | None = None) -> list[Path]:
        if not self.source_path.exists():
            return []
        paths = sorted(
            item for item in self.source_path.rglob("*")
            if item.is_file() and item.name.lower() != ".gitkeep"
        )
        return self.apply_limit(paths, limit)

    def normalize_labels(self, raw_label: str) -> tuple[str, str]:
        return "unknown", "unknown"

    def is_compatible_with_current_pipeline(self) -> bool:
        return False

    def sample_notes(self, path: Path) -> str:
        return "Dataset-specific label semantics have not been verified."
