from __future__ import annotations

from pathlib import Path

from app.datasets.adapters.custom_videos_adapter import VIDEO_EXTENSIONS
from app.datasets.base_adapter import DatasetAdapter


class SquatKaggleAdapter(DatasetAdapter):
    dataset_name = "squat_kaggle"
    modality = "unknown"

    def list_samples(self) -> list[Path]:
        if not self.source_path.exists():
            return []
        return sorted(item for item in self.source_path.rglob("*") if item.is_file() and item.suffix.lower() in VIDEO_EXTENSIONS)

    def normalize_labels(self, raw_label: str) -> tuple[str, str]:
        return "squat", "unknown"

    def is_compatible_with_current_pipeline(self) -> bool:
        # Videos alone are insufficient; a reviewed mapping must be added before enabling.
        return False

