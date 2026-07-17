from app.datasets.adapters.generic_dataset_adapter import GenericDatasetAdapter
class GenericSkeletonAdapter(GenericDatasetAdapter):
    modality="skeleton_3d";supported_modalities=("skeleton_2d","skeleton_3d")
