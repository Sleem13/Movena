from pathlib import Path
from app.datasets.adapters.custom_videos_adapter import CustomVideosAdapter
from app.datasets.adapters.squat_kaggle_adapter import SquatKaggleAdapter
from app.datasets.adapters.zenodo_squat_adapter import ZenodoSquatAdapter
from app.datasets.adapters.complex_rehab_adapters import KiMoReAdapter,UIPRMDAdapter,UCIPhysicalTherapyAdapter,DynTherapyAdapter,Rehab246Adapter,PhysicalTherapyExercisesAdapter

ADAPTERS={"custom_videos":CustomVideosAdapter,"squat_kaggle":SquatKaggleAdapter,"zenodo_squat_dataset":ZenodoSquatAdapter,"kimore":KiMoReAdapter,"ui_prmd":UIPRMDAdapter,"uci_physical_therapy_exercises":UCIPhysicalTherapyAdapter,"dyntherapy":DynTherapyAdapter,"rehab24_6":Rehab246Adapter,"Physical-therapy exercises":PhysicalTherapyExercisesAdapter}
def create_adapter(dataset_name:str,source_path:Path):
    from app.datasets.adapters.generic_dataset_adapter import GenericDatasetAdapter
    cls=ADAPTERS.get(dataset_name)
    return cls(source_path) if cls else GenericDatasetAdapter(source_path,dataset_name=dataset_name)
def registered_adapter_names():return sorted(ADAPTERS)
