"""Central registry for dataset-specific adapter construction."""

from pathlib import Path

from app.datasets.adapters.custom_videos_adapter import CustomVideosAdapter
from app.datasets.adapters.dyntherapy_adapter import DynTherapyAdapter
from app.datasets.adapters.exercise_pose_frames_adapter import ExercisePoseFramesAdapter
from app.datasets.adapters.kimore_adapter import KiMoReAdapter
from app.datasets.adapters.physical_therapy_exercises_adapter import PhysicalTherapyExercisesAdapter
from app.datasets.adapters.rehab24_6_adapter import Rehab246Adapter
from app.datasets.adapters.squat_kaggle_adapter import SquatKaggleAdapter
from app.datasets.adapters.uci_physical_therapy_adapter import UCIPhysicalTherapyAdapter
from app.datasets.adapters.uco_physical_rehab_adapter import UCOPhysicalRehabAdapter
from app.datasets.adapters.ui_prmd_adapter import UIPRMDAdapter
from app.datasets.adapters.zenodo_squat_adapter import ZenodoSquatAdapter


ADAPTERS = {
    "custom_videos": CustomVideosAdapter,
    "squat_kaggle": SquatKaggleAdapter,
    "zenodo_squat_dataset": ZenodoSquatAdapter,
    "kimore": KiMoReAdapter,
    "ui_prmd": UIPRMDAdapter,
    "uci_physical_therapy_exercises": UCIPhysicalTherapyAdapter,
    "dyntherapy": DynTherapyAdapter,
    "exercise_pose_frames": ExercisePoseFramesAdapter,
    "rehab24_6": Rehab246Adapter,
    "Physical-therapy exercises": PhysicalTherapyExercisesAdapter,
    "uco_physical_rehab": UCOPhysicalRehabAdapter,
}


def create_adapter(dataset_name: str, source_path: Path):
    from app.datasets.adapters.generic_dataset_adapter import GenericDatasetAdapter

    adapter_class = ADAPTERS.get(dataset_name)
    return adapter_class(source_path) if adapter_class else GenericDatasetAdapter(source_path, dataset_name=dataset_name)


def registered_adapter_names() -> list[str]:
    return sorted(ADAPTERS)
