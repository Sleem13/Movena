"""Discovery-only placeholders; Sprint 15 must implement verified parsing and mappings."""
from app.datasets.adapters.generic_dataset_adapter import GenericDatasetAdapter
class ManualMappingAdapter(GenericDatasetAdapter):
    requires_manual_mapping=True
    def infer_exercises(self):return ["unknown"]
class KiMoReAdapter(ManualMappingAdapter):dataset_name="kimore";modality="skeleton_3d"
class UIPRMDAdapter(ManualMappingAdapter):dataset_name="ui_prmd";modality="skeleton_3d"
class UCIPhysicalTherapyAdapter(ManualMappingAdapter):dataset_name="uci_physical_therapy_exercises";modality="sensor_timeseries"
class DynTherapyAdapter(ManualMappingAdapter):dataset_name="dyntherapy";modality="skeleton_3d"
class Rehab246Adapter(ManualMappingAdapter):dataset_name="rehab24_6";modality="mixed"
class PhysicalTherapyExercisesAdapter(ManualMappingAdapter):dataset_name="Physical-therapy exercises";modality="unknown"
