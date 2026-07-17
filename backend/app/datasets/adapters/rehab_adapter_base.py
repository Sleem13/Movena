"""Conservative helpers for rehabilitation datasets with unresolved codebooks."""

from __future__ import annotations

from pathlib import Path

from app.datasets.adapters.generic_dataset_adapter import GenericDatasetAdapter


class ManualMappingAdapter(GenericDatasetAdapter):
    """Discovery adapter that never converts an unreviewed code into an exercise."""

    requires_manual_mapping = True
    sample_extensions: frozenset[str] = frozenset()

    def list_samples(self, limit: int | None = None) -> list[Path]:
        if not self.source_path.exists():
            return []
        paths = sorted(
            path
            for path in self.source_path.rglob("*")
            if path.is_file()
            and path.name.lower() != ".gitkeep"
            and (not self.sample_extensions or path.suffix.lower() in self.sample_extensions)
        )
        return self.apply_limit(paths, limit)

    def infer_exercises(self) -> list[str]:
        return ["unknown"]

    def normalize_labels(self, raw_label: str) -> tuple[str, str]:
        return "unknown", "unknown"

    def sample_notes(self, path: Path) -> str:
        return "Exercise code and label semantics require dataset documentation review."

