"""Adapter for the optional Physical-therapy exercises folder."""

from app.datasets.adapters.rehab_adapter_base import ManualMappingAdapter


class PhysicalTherapyExercisesAdapter(ManualMappingAdapter):
    dataset_name = "Physical-therapy exercises"
    modality = "unknown"
    supported_modalities = ("video", "image", "tabular_features", "unknown")
    sample_extensions = frozenset({".mp4", ".mov", ".avi", ".mkv", ".webm", ".jpg", ".jpeg", ".png", ".csv", ".npy"})

    def sample_notes(self, path):
        return "Folder name is retained as a raw label only; exercise identity requires manual approval."

