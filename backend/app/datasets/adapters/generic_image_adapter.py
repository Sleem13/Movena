from app.datasets.adapters.generic_dataset_adapter import GenericDatasetAdapter
class GenericImageAdapter(GenericDatasetAdapter):
    modality="image";supported_modalities=("image",)
