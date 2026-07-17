"""Safe metadata adapter for the locally available KIMORE container."""

from app.datasets.adapters.rehab_adapter_base import ManualMappingAdapter


class KiMoReAdapter(ManualMappingAdapter):
    dataset_name = "kimore"
    modality = "skeleton_3d"
    supported_modalities = ("skeleton_3d", "tabular_features")
    sample_extensions = frozenset({".pkl", ".csv", ".txt", ".mat", ".npy"})

    def load_annotations(self) -> dict[str, object]:
        return {"status": "not_loaded", "reason": "Pickle content is not deserialized during metadata audit."}

