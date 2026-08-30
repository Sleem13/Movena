# data/ui_prmd_loader.py
import numpy as np
import pandas as pd
import os

from rehabrl.config import DATASETS_DIR


class UIPRMDLoader:
    """
    Loader for UI-PRMD dataset (10 rehabilitation movements, 10 healthy subjects).
    Expected folder structure: datasets/ui_prmd/SubjectXX/*.csv
    """

    def __init__(self, data_dir=None):
        self.data_dir = str(data_dir or DATASETS_DIR / "ui_prmd")
        self.joint_names = [
            "hip_flexion_l",
            "hip_flexion_r",
            "knee_angle_l",
            "knee_angle_r",
            "ankle_angle_l",
            "ankle_angle_r",
            "trunk_angle",
        ]

    def load_subject_joint_angles(self, subject_id: int, exercise: str) -> np.ndarray:
        """
        Load joint angle time series for one subject and one exercise.
        exercise: 'squat', 'lunge', 'leg_press', etc.
        Returns array of shape (time_steps, 7 joints).
        """
        # UI-PRMD filenames follow pattern: Subject01_Squat.csv
        filename = f"Subject{subject_id:02d}_{exercise.capitalize()}.csv"
        filepath = os.path.join(self.data_dir, f"Subject{subject_id:02d}", filename)
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"UI-PRMD file not found: {filepath}")

        df = pd.read_csv(filepath)
        # Select only joint angle columns (they contain 'angle' in name)
        angle_cols = [col for col in df.columns if "angle" in col.lower()]
        return df[angle_cols].values

    def compute_average_angle_profile(self, exercise: str) -> np.ndarray:
        """
        Compute average joint angle profile across all subjects for an exercise.
        Returns mean angles across the movement cycle (normalised to 0-1).
        """
        all_angles = []
        for subj in range(1, 11):  # 10 subjects
            try:
                angles = self.load_subject_joint_angles(subj, exercise)
                # Normalise time axis to 100 points
                from scipy import interpolate

                x = np.linspace(0, 1, len(angles))
                f = interpolate.interp1d(x, angles, axis=0, kind="linear")
                normalized = f(np.linspace(0, 1, 100))
                all_angles.append(normalized)
            except FileNotFoundError:
                continue
        if not all_angles:
            return np.zeros(100)
        return np.mean(all_angles, axis=0)


# Usage example
if __name__ == "__main__":
    loader = UIPRMDLoader()
    squat_profile = loader.compute_average_angle_profile("squat")
    print(f"Squat joint angle profile shape: {squat_profile.shape}")  # (100, 7)
