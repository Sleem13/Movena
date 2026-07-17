"""Adapter for UCI physical-therapy sensor/time-series text files."""

from __future__ import annotations

import re
from pathlib import Path

from app.datasets.adapters.rehab_adapter_base import ManualMappingAdapter


class UCIPhysicalTherapyAdapter(ManualMappingAdapter):
    dataset_name = "uci_physical_therapy_exercises"
    modality = "sensor_timeseries"
    supported_modalities = ("sensor_timeseries", "tabular_features")

    def list_samples(self, limit: int | None = None) -> list[Path]:
        if not self.source_path.exists():
            return []
        paths = sorted(path for path in self.source_path.rglob("test.txt") if path.is_file())
        return self.apply_limit(paths, limit)

    def _path_code(self, path: Path, prefix: str) -> str | None:
        return next((part.lower() for part in path.parts if re.fullmatch(fr"{prefix}\d+", part.lower())), None)

    def normalize_sample_metadata(self, path: Path) -> dict[str, object]:
        sample = super().normalize_sample_metadata(path)
        exercise_code = self._path_code(path, "e") or "unknown"
        sample["raw_label"] = exercise_code
        sample["participant_id"] = self._path_code(path, "s")
        user_code = self._path_code(path, "u")
        sample["session_id"] = f"{exercise_code}/{user_code}" if user_code else exercise_code
        sample["notes"] = "Sensor sample discovered; coded exercise mapping is pending codebook review."
        return sample

