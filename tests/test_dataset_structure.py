import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT / "scripts") not in sys.path:
    sys.path.insert(0, str(REPO_ROOT / "scripts"))

from check_dataset_structure import EXPECTED_DATA_DIRS


def test_expected_dataset_folder_list_contains_camera_sensor_and_fusion_paths():
    required = {
        "data/raw/custom_videos/squat_correct",
        "data/raw/custom_videos/squat_fast_uncontrolled",
        "data/raw/uci_physical_therapy_exercises",
        "data/raw/zenodo_squat_dataset",
        "data/raw/uco_physical_rehab",
        "data/processed/pose_landmarks",
        "data/processed/pose_landmarks/zenodo_squat_dataset",
        "data/processed/angle_features",
        "data/processed/angle_features/zenodo_squat_dataset",
        "data/processed/sensor_features",
        "data/processed/merged_features",
        "data/samples/squat_fast_uncontrolled",
    }

    assert required.issubset(set(EXPECTED_DATA_DIRS))


def test_expected_dataset_folders_exist_after_sprint_setup():
    missing = [folder for folder in EXPECTED_DATA_DIRS if not (REPO_ROOT / folder).exists()]

    assert missing == []
