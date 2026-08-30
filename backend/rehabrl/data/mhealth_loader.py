"""
rehab_rl/data/mhealth_loader.py
mHealth Dataset Loader and Feature Extractor.

Loads sensor data from the mHealth dataset and extracts features
suitable for the rehabilitation RL environment.
"""

import os
import numpy as np
from typing import List, Tuple, Dict
from dataclasses import dataclass


# Column indices from the mHealth dataset format
COLUMNS = {
    "chest_acc_x": 0,
    "chest_acc_y": 1,
    "chest_acc_z": 2,
    "ecg_1": 3,
    "ecg_2": 4,
    "ankle_acc_x": 5,
    "ankle_acc_y": 6,
    "ankle_acc_z": 7,
    "ankle_gyro_x": 8,
    "ankle_gyro_y": 9,
    "ankle_gyro_z": 10,
    "ankle_mag_x": 11,
    "ankle_mag_y": 12,
    "ankle_mag_z": 13,
    "wrist_acc_x": 14,
    "wrist_acc_y": 15,
    "wrist_acc_z": 16,
    "wrist_gyro_x": 17,
    "wrist_gyro_y": 18,
    "wrist_gyro_z": 19,
    "wrist_mag_x": 20,
    "wrist_mag_y": 21,
    "wrist_mag_z": 22,
}

# Activity labels in the dataset
ACTIVITY_LABELS = {
    1: "Standing still",
    2: "Sitting and relaxing",
    3: "Lying down",
    4: "Walking",
    5: "Climbing stairs",
    6: "Waist bends forward",
    7: "Frontal elevation of arms",
    8: "Knees bending",
    9: "Cycling",
    10: "Jogging",
    11: "Running",
    12: "Jump front & back",
}

# Map activities to rehabilitation-relevant categories
ACTIVITY_CATEGORIES = {
    1: "static",
    2: "static",
    3: "rest",
    4: "low_intensity",
    5: "low_intensity",
    6: "flexion",
    7: "flexion",
    8: "flexion",
    9: "cardio",
    10: "cardio",
    11: "cardio",
    12: "plyometric",
}

SAMPLING_RATE = 50  # Hz


@dataclass
class SensorWindow:
    """A window of sensor data with extracted features."""

    subject_id: int
    activity: int
    start_time: float
    end_time: float
    features: np.ndarray  # Extracted feature vector


class MHealthLoader:
    """Loads and processes mHealth dataset files."""

    def __init__(self, data_dir: str):
        self.data_dir = data_dir
        self.subject_files = [
            f
            for f in os.listdir(data_dir)
            if f.startswith("mHealth_subject") and f.endswith(".log")
        ]

    def load_subject(self, subject_id: int) -> np.ndarray:
        """Load data for a specific subject."""
        filepath = os.path.join(self.data_dir, f"mHealth_subject{subject_id}.log")
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"Subject file not found: {filepath}")

        # Load CSV-like data (tab or space separated)
        # Try tab first, then space
        try:
            data = np.loadtxt(filepath, delimiter="\t")
        except ValueError:
            data = np.loadtxt(filepath, delimiter=" ")
        return data

    def load_all_subjects(self) -> Dict[int, np.ndarray]:
        """Load data from all subjects."""
        all_data = {}
        for f in self.subject_files:
            # Extract subject ID from filename
            subject_id = int(f.replace("mHealth_subject", "").replace(".log", ""))
            all_data[subject_id] = self.load_subject(subject_id)
        return all_data

    def extract_window_features(
        self,
        window: np.ndarray,
        _window_size: int = 50,  # 1 second at 50Hz (kept for API compatibility)
    ) -> np.ndarray:
        """
        Extract statistical features from a window of sensor data.

        Features extracted:
        - Mean, std, min, max for each sensor axis
        - Signal magnitude area
        - Correlation between axes
        - Frequency domain features (dominant frequency)

        Returns a feature vector of shape (n_features,)
        """
        features = []

        # Define sensor groups
        sensors = {
            "chest": window[:, 0:3],
            "ankle": window[:, 5:7],  # acc only
            "wrist": window[:, 14:17],  # acc only
        }

        for _sensor_name, sensor_data in sensors.items():
            if sensor_data.shape[0] == 0:
                continue

            # Time domain features
            features.extend(np.mean(sensor_data, axis=0))  # 3 means
            features.extend(np.std(sensor_data, axis=0))  # 3 stds
            features.extend(np.min(sensor_data, axis=0))  # 3 mins
            features.extend(np.max(sensor_data, axis=0))  # 3 maxs

            # Signal magnitude area
            sma = np.sum(np.abs(sensor_data), axis=0).mean()
            features.append(sma)

        # Activity intensity feature (based on overall movement)
        total_movement = np.sum(np.abs(window[:, 5:8])) + np.sum(
            np.abs(window[:, 14:17])
        )
        features.append(total_movement / (window.shape[0] * 6))

        return np.array(features, dtype=np.float32)

    def segment_by_activity(
        self, data: np.ndarray, min_window_size: int = 50
    ) -> List[Tuple[int, np.ndarray]]:
        """
        Segment data by activity labels.
        Returns list of (activity_label, data_segment) tuples.
        """
        if data.shape[1] < 23:
            raise ValueError("Data doesn't have enough columns for activity label")

        activity_col = 23  # Last column is activity label
        activities = data[:, activity_col].astype(int)

        segments = []
        current_activity = activities[0]
        current_start = 0

        for i in range(len(activities)):
            if activities[i] != current_activity:
                if i - current_start >= min_window_size:
                    segments.append((current_activity, data[current_start:i]))
                current_activity = activities[i]
                current_start = i

        # Add last segment
        if len(activities) - current_start >= min_window_size:
            segments.append((current_activity, data[current_start:]))

        return segments

    def create_training_windows(
        self,
        window_size: int = 50,  # 1 second windows
        stride: int = 25,  # 50% overlap
    ) -> List[SensorWindow]:
        """
        Create sliding window dataset from all subjects.
        """
        windows = []

        for subject_id in range(1, 11):  # Subjects 1-10
            try:
                data = self.load_subject(subject_id)
            except FileNotFoundError:
                continue

            segments = self.segment_by_activity(data)

            for activity, segment in segments:
                # Create sliding windows
                for start in range(0, len(segment) - window_size, stride):
                    window_data = segment[start : start + window_size]
                    features = self.extract_window_features(window_data, window_size)

                    windows.append(
                        SensorWindow(
                            subject_id=subject_id,
                            activity=activity,
                            start_time=start / SAMPLING_RATE,
                            end_time=(start + window_size) / SAMPLING_RATE,
                            features=features,
                        )
                    )

        return windows

    def get_activity_statistics(self) -> Dict[int, Dict]:
        """Get statistics for each activity across all subjects."""
        all_data = self.load_all_subjects()
        stats = {act: {"count": 0, "subjects": set()} for act in ACTIVITY_LABELS}

        for subject_id, data in all_data.items():
            if data.shape[1] < 24:
                continue
            activities = data[:, 23].astype(int)
            for act in np.unique(activities):
                if act in stats:
                    stats[act]["count"] += np.sum(activities == act)
                    stats[act]["subjects"].add(subject_id)

        return stats


def load_mhealth_data(data_dir: str) -> List[SensorWindow]:
    """
    Convenience function to load all mHealth data as feature windows.
    """
    loader = MHealthLoader(data_dir)
    return loader.create_training_windows()


# Map mHealth activities to rehabilitation metrics
def activity_to_rehab_metrics(activity: int) -> Dict[str, float]:
    """
    Map an mHealth activity to estimated rehabilitation metrics.
    These can be used to initialize or validate the RL environment.

    Returns dict with keys:
    - intensity: 0-1 scale of exercise intensity
    - rom_benefit: range of motion improvement potential
    - strength_benefit: strength improvement potential
    - cardio_benefit: cardiovascular improvement
    - fatigue: fatigue/exertion level
    - pain_risk: risk of pain exacerbation
    - stage: suitable recovery stage (0-4)
    """
    category = ACTIVITY_CATEGORIES.get(activity, "unknown")

    # Estimated intensity and benefit metrics
    mapping = {
        "static": {
            "intensity": 0.2,
            "rom_benefit": 0.1,
            "strength_benefit": 0.05,
            "cardio_benefit": 0.1,
            "fatigue": 0.05,
            "pain_risk": 0.1,
            "stage": 0,
        },
        "rest": {
            "intensity": 0.05,
            "rom_benefit": 0.0,
            "strength_benefit": 0.0,
            "cardio_benefit": 0.0,
            "fatigue": 0.0,
            "pain_risk": 0.0,
            "stage": 0,
        },
        "low_intensity": {
            "intensity": 0.4,
            "rom_benefit": 0.3,
            "strength_benefit": 0.2,
            "cardio_benefit": 0.3,
            "fatigue": 0.3,
            "pain_risk": 0.15,
            "stage": 1,
        },
        "flexion": {
            "intensity": 0.5,
            "rom_benefit": 0.6,
            "strength_benefit": 0.3,
            "cardio_benefit": 0.2,
            "fatigue": 0.4,
            "pain_risk": 0.25,
            "stage": 2,
        },
        "cardio": {
            "intensity": 0.8,
            "rom_benefit": 0.2,
            "strength_benefit": 0.4,
            "cardio_benefit": 0.8,
            "fatigue": 0.7,
            "pain_risk": 0.3,
            "stage": 3,
        },
        "plyometric": {
            "intensity": 0.9,
            "rom_benefit": 0.4,
            "strength_benefit": 0.6,
            "cardio_benefit": 0.6,
            "fatigue": 0.8,
            "pain_risk": 0.4,
            "stage": 4,
        },
    }

    result = mapping.get(
        category,
        {
            "intensity": 0.5,
            "rom_benefit": 0.3,
            "strength_benefit": 0.3,
            "cardio_benefit": 0.3,
            "fatigue": 0.4,
            "pain_risk": 0.2,
            "stage": 2,
        },
    )
    return result
