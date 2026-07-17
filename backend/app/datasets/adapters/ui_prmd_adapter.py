"""Conservative UI-PRMD skeleton metadata adapter."""

from pathlib import Path

from app.datasets.adapters.rehab_adapter_base import ManualMappingAdapter


class UIPRMDAdapter(ManualMappingAdapter):
    dataset_name = "ui_prmd"
    modality = "skeleton_3d"
    supported_modalities = ("skeleton_3d", "tabular_features")
    sample_extensions = frozenset({".csv", ".save", ".txt", ".npy"})

    def list_samples(self, limit: int | None = None) -> list[Path]:
        paths = super().list_samples()
        paths = [path for path in paths if path.name.lower() != "label.csv"]
        return self.apply_limit(paths, limit)

    def load_annotations(self) -> dict[str, object]:
        label_file = self.source_path / "label.csv"
        return {"label_file": str(label_file), "available": label_file.is_file(), "status": "needs_codebook_review"}

