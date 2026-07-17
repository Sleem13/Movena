"""Initial dataset adapter implementations."""

from app.datasets.adapters.custom_videos_adapter import CustomVideosAdapter
from app.datasets.adapters.dyntherapy_adapter import DynTherapyAdapter
from app.datasets.adapters.generic_dataset_adapter import GenericDatasetAdapter
from app.datasets.adapters.kimore_adapter import KiMoReAdapter
from app.datasets.adapters.physical_therapy_exercises_adapter import PhysicalTherapyExercisesAdapter
from app.datasets.adapters.rehab24_6_adapter import Rehab246Adapter
from app.datasets.adapters.squat_kaggle_adapter import SquatKaggleAdapter
from app.datasets.adapters.uci_physical_therapy_adapter import UCIPhysicalTherapyAdapter
from app.datasets.adapters.uco_physical_rehab_adapter import UCOPhysicalRehabAdapter
from app.datasets.adapters.ui_prmd_adapter import UIPRMDAdapter
from app.datasets.adapters.zenodo_squat_adapter import ZenodoSquatAdapter

__all__ = [
    "CustomVideosAdapter", "GenericDatasetAdapter", "SquatKaggleAdapter", "ZenodoSquatAdapter",
    "KiMoReAdapter", "UIPRMDAdapter", "UCIPhysicalTherapyAdapter", "DynTherapyAdapter",
    "Rehab246Adapter", "PhysicalTherapyExercisesAdapter", "UCOPhysicalRehabAdapter",
]
