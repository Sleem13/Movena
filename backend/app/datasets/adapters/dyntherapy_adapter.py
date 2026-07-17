"""Discovery adapter for the local DynTherapy feature container."""

from app.datasets.adapters.rehab_adapter_base import ManualMappingAdapter


class DynTherapyAdapter(ManualMappingAdapter):
    dataset_name = "dyntherapy"
    modality = "skeleton_3d"
    supported_modalities = ("skeleton_3d", "tabular_features")
    sample_extensions = frozenset({".csv", ".npy", ".txt"})

    def sample_notes(self, path):
        return "Pose-feature container discovered; row schema and exercise labels require review before sequence extraction."

