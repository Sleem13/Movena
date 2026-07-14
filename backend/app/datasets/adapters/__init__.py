"""Initial dataset adapter implementations."""

from app.datasets.adapters.custom_videos_adapter import CustomVideosAdapter
from app.datasets.adapters.generic_dataset_adapter import GenericDatasetAdapter
from app.datasets.adapters.squat_kaggle_adapter import SquatKaggleAdapter
from app.datasets.adapters.zenodo_squat_adapter import ZenodoSquatAdapter

__all__ = ["CustomVideosAdapter", "GenericDatasetAdapter", "SquatKaggleAdapter", "ZenodoSquatAdapter"]

