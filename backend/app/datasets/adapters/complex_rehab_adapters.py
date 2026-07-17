"""Backward-compatible imports for the Sprint 14 placeholder module."""

from app.datasets.adapters.dyntherapy_adapter import DynTherapyAdapter
from app.datasets.adapters.kimore_adapter import KiMoReAdapter
from app.datasets.adapters.physical_therapy_exercises_adapter import PhysicalTherapyExercisesAdapter
from app.datasets.adapters.rehab24_6_adapter import Rehab246Adapter
from app.datasets.adapters.rehab_adapter_base import ManualMappingAdapter
from app.datasets.adapters.uci_physical_therapy_adapter import UCIPhysicalTherapyAdapter
from app.datasets.adapters.ui_prmd_adapter import UIPRMDAdapter

__all__ = [
    "ManualMappingAdapter",
    "KiMoReAdapter",
    "UIPRMDAdapter",
    "UCIPhysicalTherapyAdapter",
    "DynTherapyAdapter",
    "Rehab246Adapter",
    "PhysicalTherapyExercisesAdapter",
]
