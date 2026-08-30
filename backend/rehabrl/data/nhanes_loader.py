"""
rehab_rl/data/nhanes_loader.py
NHANES (National Health and Nutrition Examination Survey) Data Loader

Loads clinical baseline data for validation and benchmarking.
Creates healthy population baselines for ROM, strength, and other metrics.

Note: This generates synthetic NHANES-like data matching real distributions.
For production, replace with actual NHANES data download.
"""

import numpy as np
from dataclasses import dataclass
from typing import Dict, List, Tuple


@dataclass
class NHANESRecord:
    """Single NHANES health record."""

    age: int  # 18-85
    sex: str  # 'M' or 'F'
    bmi: float  # Body Mass Index
    pain_score: float  # 0-10 (any joint pain)
    rom_score: float  # 0-100 (range of motion, normalized)
    grip_strength: float  # kg (hand grip strength)
    mobility_score: float  # 0-100 (mobility assessment)
    flexibility: float  # 0-100 (flexibility/ROM)
    injury_history: bool  # Had injury/surgery in past
    activity_level: str  # 'Sedentary', 'Low', 'Moderate', 'High'


class NHANESBaselineGenerator:
    """
    Generates synthetic NHANES-like baseline data.

    Matches real population statistics from NHANES cycles:
    - Age distribution in US
    - Gender distribution
    - ROM/strength by age and sex
    - Injury prevalence
    - Activity levels
    """

    def __init__(self, n_records: int = 1000, seed: int = 42):
        self.n_records = n_records
        self.rng = np.random.default_rng(seed)
        self.records: List[NHANESRecord] = []

    def _age_distribution(self) -> int:
        """Age distribution (skewed toward older in NHANES)."""
        # Beta distribution: more people in 45-65 range
        age = self.rng.beta(2, 2) * 67 + 18  # 18-85
        return int(age)

    def _sex_distribution(self) -> str:
        """Gender distribution (~50/50)."""
        return "M" if self.rng.random() < 0.5 else "F"

    def _bmi_by_age_sex(self, age: int, sex: str) -> float:
        """BMI distribution by age and sex (realistic US data)."""
        if sex == "M":
            base_bmi = 28.5 if age > 50 else 27.5
        else:
            base_bmi = 29.0 if age > 50 else 27.0

        # Add noise
        bmi = base_bmi + self.rng.normal(0, 2.5)
        return np.clip(bmi, 15, 50)  # Realistic bounds

    def _rom_by_age_sex(
        self, age: int, sex: str, bmi: float, injury_history: bool
    ) -> float:
        """ROM decreases with age, varies by sex."""
        # Women generally have better ROM than men
        sex_factor = 0.95 if sex == "F" else 1.0

        # ROM decreases with age (linear decline)
        age_factor = 1.0 - (age - 18) / 67 * 0.3

        # BMI slightly negatively affects ROM
        bmi_factor = 1.0 - max(0, (bmi - 25) / 25 * 0.15)

        # Injury history reduces ROM
        injury_factor = 0.8 if injury_history else 1.0

        base_rom = 85  # Baseline ROM score
        rom = base_rom * sex_factor * age_factor * bmi_factor * injury_factor

        # Add noise
        rom = rom + self.rng.normal(0, 8)
        return np.clip(rom, 20, 100)

    def _strength_by_age_sex(
        self, age: int, sex: str, bmi: float, injury_history: bool
    ) -> float:
        """Grip strength by age and sex (kg)."""
        # Base grip strength by sex (NHANES data)
        if sex == "M":
            base_strength = 48  # kg (males)
        else:
            base_strength = 30  # kg (females)

        # Strength decreases with age (accelerates after 50)
        if age < 50:
            age_factor = 1.0 - (age - 18) / 32 * 0.1
        else:
            age_factor = 0.9 - (age - 50) / 35 * 0.4

        # BMI has weak positive correlation with strength (up to 30)
        bmi_factor = 1.0 + max(0, min((bmi - 25) / 10 * 0.2, 0.2))

        # Injury reduces strength
        injury_factor = 0.85 if injury_history else 1.0

        strength = base_strength * age_factor * bmi_factor * injury_factor

        # Add noise
        strength = strength + self.rng.normal(0, 4)
        return np.clip(strength, 5, 70)

    def _pain_by_age_injury(self, age: int, injury_history: bool) -> float:
        """Joint pain prevalence and severity."""
        # Pain increases with age
        age_factor = (age - 18) / 67 * 0.4  # 0-0.4

        # Injury history increases pain
        if injury_history:
            pain = self.rng.beta(2, 5) * 5 + 2  # Mean ~3
        else:
            pain = self.rng.beta(1, 5) * 2  # Mean ~0.5

        pain = pain + age_factor * 2
        return np.clip(pain, 0, 10)

    def _activity_level(self) -> str:
        """Distribution of activity levels."""
        r = self.rng.random()
        if r < 0.30:
            return "Sedentary"
        elif r < 0.55:
            return "Low"
        elif r < 0.85:
            return "Moderate"
        else:
            return "High"

    def _injury_history(self, age: int) -> bool:
        """Injury/surgery prevalence increases with age."""
        prevalence = 0.05 + (age - 18) / 67 * 0.30  # 5-35%
        return self.rng.random() < prevalence

    def generate(self) -> List[NHANESRecord]:
        """Generate synthetic NHANES dataset."""
        self.records = []

        for _ in range(self.n_records):
            age = self._age_distribution()
            sex = self._sex_distribution()
            bmi = self._bmi_by_age_sex(age, sex)
            injury_history = self._injury_history(age)

            rom = self._rom_by_age_sex(age, sex, bmi, injury_history)
            strength = self._strength_by_age_sex(age, sex, bmi, injury_history)
            pain = self._pain_by_age_injury(age, injury_history)

            mobility = rom * 0.6 + 50  # Composite score
            flexibility = rom

            activity_level = self._activity_level()

            record = NHANESRecord(
                age=age,
                sex=sex,
                bmi=bmi,
                pain_score=pain,
                rom_score=rom,
                grip_strength=strength,
                mobility_score=mobility,
                flexibility=flexibility,
                injury_history=injury_history,
                activity_level=activity_level,
            )
            self.records.append(record)

        return self.records

    def get_healthy_baseline(self) -> Dict[str, float]:
        """
        Get baseline metrics for healthy (no injury history) population.
        Used for normalizing agent recommendations.
        """
        healthy = [r for r in self.records if not r.injury_history]

        if not healthy:
            return {}

        healthy_array = np.array(
            [
                [r.age, r.rom_score, r.grip_strength, r.flexibility, r.mobility_score]
                for r in healthy
            ]
        )

        return {
            "age_mean": float(np.mean(healthy_array[:, 0])),
            "rom_mean": float(np.mean(healthy_array[:, 1])),
            "rom_std": float(np.std(healthy_array[:, 1])),
            "strength_mean": float(np.mean(healthy_array[:, 2])),
            "strength_std": float(np.std(healthy_array[:, 2])),
            "flexibility_mean": float(np.mean(healthy_array[:, 3])),
            "mobility_mean": float(np.mean(healthy_array[:, 4])),
            "pain_mean": float(np.mean([r.pain_score for r in healthy])),
        }

    def get_baselines_by_age_group(self) -> Dict[str, Dict]:
        """
        Get baselines by age group for more granular validation.
        """
        age_groups = {
            "18-30": (18, 30),
            "31-45": (31, 45),
            "46-60": (46, 60),
            "61+": (61, 85),
        }

        baselines = {}
        for group_name, (min_age, max_age) in age_groups.items():
            group_records = [
                r
                for r in self.records
                if min_age <= r.age <= max_age and not r.injury_history
            ]

            if not group_records:
                continue

            baselines[group_name] = {
                "n": len(group_records),
                "rom_mean": np.mean([r.rom_score for r in group_records]),
                "rom_std": np.std([r.rom_score for r in group_records]),
                "strength_mean": np.mean([r.grip_strength for r in group_records]),
                "strength_std": np.std([r.grip_strength for r in group_records]),
                "flexibility_mean": np.mean([r.flexibility for r in group_records]),
                "pain_mean": np.mean([r.pain_score for r in group_records]),
            }

        return baselines

    def get_injured_vs_healthy_comparison(self) -> Dict[str, Dict]:
        """
        Compare injured vs healthy populations.
        Useful for validating rehabilitation improvements.
        """
        healthy = [r for r in self.records if not r.injury_history]
        injured = [r for r in self.records if r.injury_history]

        def compute_stats(records):
            return {
                "n": len(records),
                "age_mean": np.mean([r.age for r in records]),
                "rom_mean": np.mean([r.rom_score for r in records]),
                "rom_std": np.std([r.rom_score for r in records]),
                "strength_mean": np.mean([r.grip_strength for r in records]),
                "strength_std": np.std([r.grip_strength for r in records]),
                "pain_mean": np.mean([r.pain_score for r in records]),
                "pain_std": np.std([r.pain_score for r in records]),
                "mobility_mean": np.mean([r.mobility_score for r in records]),
            }

        return {
            "healthy": compute_stats(healthy),
            "injured": compute_stats(injured),
        }


class NHANESLoader:
    """
    Interface for loading NHANES data and comparing agent against baselines.
    """

    def __init__(self, n_records: int = 1000, seed: int = 42):
        self.generator = NHANESBaselineGenerator(n_records, seed)
        self.data = None

    def load_data(self) -> List[NHANESRecord]:
        """Generate and load NHANES data."""
        self.data = self.generator.generate()
        return self.data

    def get_healthy_baseline(self) -> Dict:
        """Get healthy population baseline metrics."""
        if self.data is None:
            self.load_data()
        return self.generator.get_healthy_baseline()

    def get_baselines_by_age(self) -> Dict:
        """Get baselines by age group."""
        if self.data is None:
            self.load_data()
        return self.generator.get_baselines_by_age_group()

    def get_injured_vs_healthy(self) -> Dict:
        """Compare injured vs healthy populations."""
        if self.data is None:
            self.load_data()
        return self.generator.get_injured_vs_healthy_comparison()

    def normalize_metrics(
        self, rom: float, strength: float, age: int = 45, sex: str = "M"
    ) -> Tuple[float, float]:
        """
        Normalize agent recommendations against healthy population baseline.

        Returns: (rom_percentile, strength_percentile)
        where 0.5 = median, 0.9 = 90th percentile, etc.
        """
        baseline = self.get_healthy_baseline()

        rom_percentile = self._percentile_from_normal(
            rom, baseline["rom_mean"], baseline["rom_std"]
        )
        strength_percentile = self._percentile_from_normal(
            strength, baseline["strength_mean"], baseline["strength_std"]
        )

        return rom_percentile, strength_percentile

    @staticmethod
    def _percentile_from_normal(value: float, mean: float, std: float) -> float:
        """Convert normal distribution value to percentile (0-1)."""
        from scipy import stats

        return float(stats.norm.cdf(value, loc=mean, scale=std))


# Convenience function
def load_nhanes_baselines(n_records: int = 1000) -> Dict:
    """
    Load NHANES baselines for agent validation.
    """
    loader = NHANESLoader(n_records)
    loader.load_data()

    return {
        "healthy_baseline": loader.get_healthy_baseline(),
        "by_age": loader.get_baselines_by_age(),
        "injured_vs_healthy": loader.get_injured_vs_healthy(),
    }
