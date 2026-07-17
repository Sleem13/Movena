from app.datasets.adapters.generic_dataset_adapter import GenericDatasetAdapter
class GenericSensorAdapter(GenericDatasetAdapter):
    modality="sensor_timeseries";supported_modalities=("sensor_timeseries",)
