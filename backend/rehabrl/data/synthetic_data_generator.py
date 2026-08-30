"""
rehab_rl/data/synthetic_data_generator.py
==========================================
Clinically-Grounded Synthetic Patient Data Generator

Generates realistic rehabilitation outcome data for all 12 injury types
using evidence-based recovery curves, matched exactly to the RehabRL
state space and reward function:

    R = 0.30×ΔPain + 0.20×ΔROM + 0.20×ΔStrength
      + 0.15×Adherence + 0.15×Safety

Outputs
-------
- CSV / JSON patient trajectory datasets
- NumPy arrays ready for RL training
- Per-injury recovery profile statistics
- Validation splits (train / val / test)

Usage
-----
    from rehabrl.data.synthetic_data_generator import RehabDataGenerator

    gen = RehabDataGenerator(seed=42)
    df  = gen.generate_dataset(n_patients=500)
    df.to_csv("data/rehab_synthetic.csv", index=False)

    X_train, X_val, X_test = gen.get_rl_arrays(n_patients=500)
"""

import numpy as np
import pandas as pd
import os
from dataclasses import dataclass, asdict
from typing import Dict, List, Optional, Tuple

from rehabrl.config import SYNTHETIC_DATA_DIR

# ── Injury profile constants ─────────────────────────────────────────────────
# Each profile encodes evidence-based recovery characteristics:
#   initial_pain   : mean starting pain (0–1)
#   initial_rom    : mean starting ROM (0–1)
#   initial_str    : mean starting strength (0–1)
#   recovery_weeks : median weeks to full recovery
#   pain_decay     : rate of pain reduction per session (logistic scale)
#   rom_growth     : rate of ROM gain per session
#   str_growth     : rate of strength gain per session
#   severity_range : (min, max) injury severity distribution
#   adherence_base : typical adherence for this injury
#   dropout_risk   : probability of reduced adherence over time
#   overtraining_sensitivity : how easily overtraining occurs
#   notes          : clinical reference

INJURY_PROFILES: Dict[str, Dict] = {
    "ACL Tear": {
        "initial_pain": (0.65, 0.85),
        "initial_rom": (0.20, 0.45),
        "initial_str": (0.25, 0.45),
        "recovery_weeks": 36,
        "pain_decay": 0.025,
        "rom_growth": 0.030,
        "str_growth": 0.028,
        "severity_range": (0.6, 1.0),
        "adherence_base": 0.82,
        "dropout_risk": 0.12,
        "overtraining_sensitivity": 0.7,
        "notes": "Shelbourne & Nitz 1992; typical 9-month return-to-sport",
    },
    "Rotator Cuff Tear": {
        "initial_pain": (0.55, 0.80),
        "initial_rom": (0.30, 0.55),
        "initial_str": (0.30, 0.50),
        "recovery_weeks": 24,
        "pain_decay": 0.030,
        "rom_growth": 0.025,
        "str_growth": 0.022,
        "severity_range": (0.5, 0.9),
        "adherence_base": 0.78,
        "dropout_risk": 0.15,
        "overtraining_sensitivity": 0.6,
        "notes": "Ainsworth & Lewis 2004; 6-month conservative rehab",
    },
    "Lumbar Disc Herniation": {
        "initial_pain": (0.70, 0.90),
        "initial_rom": (0.25, 0.50),
        "initial_str": (0.35, 0.55),
        "recovery_weeks": 16,
        "pain_decay": 0.035,
        "rom_growth": 0.020,
        "str_growth": 0.018,
        "severity_range": (0.5, 0.9),
        "adherence_base": 0.75,
        "dropout_risk": 0.20,
        "overtraining_sensitivity": 0.8,
        "notes": "Saal & Saal 1989; 4-month conservative management",
    },
    "Ankle Sprain": {
        "initial_pain": (0.40, 0.65),
        "initial_rom": (0.45, 0.65),
        "initial_str": (0.50, 0.70),
        "recovery_weeks": 6,
        "pain_decay": 0.060,
        "rom_growth": 0.055,
        "str_growth": 0.045,
        "severity_range": (0.2, 0.7),
        "adherence_base": 0.88,
        "dropout_risk": 0.08,
        "overtraining_sensitivity": 0.4,
        "notes": "Kerkhoffs et al. 2002; Grade II-III sprains 4-8 weeks",
    },
    "Tennis Elbow": {
        "initial_pain": (0.55, 0.75),
        "initial_rom": (0.60, 0.80),
        "initial_str": (0.40, 0.60),
        "recovery_weeks": 12,
        "pain_decay": 0.040,
        "rom_growth": 0.015,
        "str_growth": 0.030,
        "severity_range": (0.3, 0.7),
        "adherence_base": 0.80,
        "dropout_risk": 0.18,
        "overtraining_sensitivity": 0.65,
        "notes": "Bisset et al. 2006; eccentric loading protocol",
    },
    "Patellofemoral Syndrome": {
        "initial_pain": (0.50, 0.70),
        "initial_rom": (0.50, 0.70),
        "initial_str": (0.40, 0.60),
        "recovery_weeks": 10,
        "pain_decay": 0.040,
        "rom_growth": 0.030,
        "str_growth": 0.035,
        "severity_range": (0.3, 0.7),
        "adherence_base": 0.84,
        "dropout_risk": 0.10,
        "overtraining_sensitivity": 0.55,
        "notes": "Crossley et al. 2001; VMO strengthening protocol",
    },
    "Hip Labral Tear": {
        "initial_pain": (0.55, 0.78),
        "initial_rom": (0.30, 0.55),
        "initial_str": (0.35, 0.55),
        "recovery_weeks": 20,
        "pain_decay": 0.032,
        "rom_growth": 0.028,
        "str_growth": 0.025,
        "severity_range": (0.5, 0.9),
        "adherence_base": 0.79,
        "dropout_risk": 0.14,
        "overtraining_sensitivity": 0.65,
        "notes": "Byrd & Jones 2004; arthroscopic + conservative",
    },
    "Achilles Tendinopathy": {
        "initial_pain": (0.50, 0.72),
        "initial_rom": (0.50, 0.70),
        "initial_str": (0.35, 0.55),
        "recovery_weeks": 16,
        "pain_decay": 0.030,
        "rom_growth": 0.025,
        "str_growth": 0.032,
        "severity_range": (0.4, 0.8),
        "adherence_base": 0.81,
        "dropout_risk": 0.13,
        "overtraining_sensitivity": 0.70,
        "notes": "Alfredson et al. 1998; eccentric calf raise protocol",
    },
    "Shoulder Impingement": {
        "initial_pain": (0.45, 0.68),
        "initial_rom": (0.40, 0.65),
        "initial_str": (0.40, 0.60),
        "recovery_weeks": 12,
        "pain_decay": 0.038,
        "rom_growth": 0.028,
        "str_growth": 0.025,
        "severity_range": (0.3, 0.7),
        "adherence_base": 0.82,
        "dropout_risk": 0.11,
        "overtraining_sensitivity": 0.55,
        "notes": "Michener et al. 2004; rotator cuff + scapular stabilisation",
    },
    "Plantar Fasciitis": {
        "initial_pain": (0.55, 0.75),
        "initial_rom": (0.60, 0.80),
        "initial_str": (0.55, 0.75),
        "recovery_weeks": 10,
        "pain_decay": 0.042,
        "rom_growth": 0.015,
        "str_growth": 0.020,
        "severity_range": (0.3, 0.7),
        "adherence_base": 0.76,
        "dropout_risk": 0.22,
        "overtraining_sensitivity": 0.60,
        "notes": "DiGiovanni et al. 2003; stretching & orthotics",
    },
    "Cervical Strain": {
        "initial_pain": (0.60, 0.80),
        "initial_rom": (0.35, 0.60),
        "initial_str": (0.40, 0.60),
        "recovery_weeks": 8,
        "pain_decay": 0.045,
        "rom_growth": 0.035,
        "str_growth": 0.025,
        "severity_range": (0.3, 0.8),
        "adherence_base": 0.77,
        "dropout_risk": 0.19,
        "overtraining_sensitivity": 0.65,
        "notes": "Verhagen et al. 2007; active exercise vs collar",
    },
    "Hamstring Strain": {
        "initial_pain": (0.55, 0.75),
        "initial_rom": (0.35, 0.60),
        "initial_str": (0.30, 0.55),
        "recovery_weeks": 8,
        "pain_decay": 0.050,
        "rom_growth": 0.040,
        "str_growth": 0.038,
        "severity_range": (0.3, 0.8),
        "adherence_base": 0.85,
        "dropout_risk": 0.09,
        "overtraining_sensitivity": 0.60,
        "notes": "Askling et al. 2003; lengthening vs conventional exercise",
    },
}

# ── Prescription action templates (mirrors ACTION_SPACE in exercise_database.py) ─
PRESCRIPTION_PROFILES = [
    # (stage, intensity, progression, name)
    # Stage 0 – Acute
    (0, "Low", "Maintain", "Acute Rest & RICE"),
    (0, "Low", "Progress", "Gentle ROM Exercises"),
    (0, "Moderate", "Maintain", "Isometric Strengthening"),
    (0, "Moderate", "Progress", "Aquatic Therapy"),
    (0, "Low", "Regress", "Pain Management Focus"),
    (0, "Low", "Maintain", "Electrotherapy Support"),
    # Stage 1 – Subacute
    (1, "Low", "Progress", "Gentle Strengthening"),
    (1, "Moderate", "Maintain", "ROM & Flexibility"),
    (1, "Moderate", "Progress", "Progressive Resistance"),
    (1, "Low", "Maintain", "Balance Training Intro"),
    (1, "Moderate", "Maintain", "Functional Movements"),
    (1, "High", "Maintain", "Hydrotherapy Progression"),
    # Stage 2 – Remodeling
    (2, "Moderate", "Progress", "Resistance Training"),
    (2, "High", "Maintain", "Cardiovascular Conditioning"),
    (2, "Moderate", "Maintain", "Proprioception Training"),
    (2, "High", "Progress", "Agility Drills"),
    (2, "Moderate", "Regress", "Mobility Focus"),
    (2, "High", "Maintain", "Core Stabilisation"),
    # Stage 3 – Functional
    (3, "High", "Progress", "Sport-Specific Training"),
    (3, "Moderate", "Maintain", "Functional Strength"),
    (3, "High", "Maintain", "Plyometric Introduction"),
    (3, "High", "Progress", "Advanced Agility"),
    (3, "Moderate", "Progress", "Power Training"),
    (3, "High", "Maintain", "Neuromuscular Control"),
    # Stage 4 – Return
    (4, "High", "Progress", "Return-to-Sport Protocol"),
    (4, "High", "Maintain", "Performance Optimisation"),
    (4, "Moderate", "Maintain", "Maintenance Programme"),
    (4, "High", "Progress", "Advanced Conditioning"),
    (4, "Moderate", "Regress", "Deload Week"),
    (4, "High", "Maintain", "Full Activity Clearance"),
]

# Stage advancement thresholds (from environment.py)
STAGE_THRESHOLDS = [0.50, 0.62, 0.74, 0.85]

# ── Data containers ───────────────────────────────────────────────────────────


@dataclass
class SessionRecord:
    """One rehabilitation session record."""

    patient_id: int
    session_number: int
    injury_type: str
    injury_severity: float
    recovery_stage: int
    stage_name: str
    pain_level: float
    pain_vas: float  # VAS 0–10 scale for clinical reporting
    rom: float  # 0–1 normalised
    rom_pct: float  # 0–100 % for reporting
    strength: float  # 0–1
    strength_pct: float  # 0–100 %
    movement_quality: float
    fatigue: float
    adherence: float
    adherence_pct: float
    days_since_last: int
    composite_score: float  # (ROM + Strength) / 2
    prescription_id: int
    prescription_name: str
    prescription_stage: int
    intensity: str
    progression: str
    # Reward components (mirror RewardFunction.compute)
    r_pain: float
    r_rom: float
    r_strength: float
    r_adherence: float
    r_safety: float
    reward_total: float
    overtraining: bool
    recovered: bool
    # Delta metrics (for analysis)
    delta_pain: float
    delta_rom: float
    delta_strength: float


# ── Main Generator ─────────────────────────────────────────────────────────────


class RehabDataGenerator:
    """
    Generates clinically-grounded rehabilitation patient trajectories.

    Each patient follows an evidence-based recovery arc shaped by:
      - Injury-specific recovery profile (pain decay, ROM growth rates)
      - Severity-dependent initial conditions
      - Stochastic noise (inter-patient variability σ=0.04)
      - Adherence dropouts and overtraining events
      - Prescription matching quality (stage, intensity)
      - Reward function identical to RehabEnvironment

    Parameters
    ----------
    seed : int
        Random seed for reproducibility.
    noise_std : float
        Gaussian noise on all state transitions (default 0.04).
    max_sessions : int
        Maximum sessions per episode (default 50).
    recovery_threshold : float
        Composite score to graduate to full recovery (default 0.85).
    """

    INJURY_TYPES = list(INJURY_PROFILES.keys())
    STAGE_NAMES = ["Acute", "Subacute", "Remodeling", "Functional", "Return"]

    # Reward weights — identical to EnvConfig
    W_PAIN = 0.30
    W_ROM = 0.20
    W_STRENGTH = 0.20
    W_ADHERENCE = 0.15
    W_SAFETY = 0.15

    def __init__(
        self,
        seed: int = 42,
        noise_std: float = 0.04,
        max_sessions: int = 50,
        recovery_threshold: float = 0.85,
    ):
        self.rng = np.random.default_rng(seed)
        self.noise_std = noise_std
        self.max_sessions = max_sessions
        self.recovery_threshold = recovery_threshold

    # ── Internal helpers ──────────────────────────────────────────────────

    def _noise(self, scale: float = 1.0) -> float:
        return float(self.rng.normal(0, self.noise_std * scale))

    def _sigmoid_recovery(
        self,
        x: float,
        rate: float,
        shift: float = 0.0,
    ) -> float:
        """Logistic growth curve: models natural recovery plateau."""
        return 1.0 / (1.0 + np.exp(-rate * (x - shift)))

    def _select_prescription(self, stage: int, pain: float, fatigue: float) -> int:
        """
        Choose a clinically-appropriate prescription action.

        Logic:
        - In Acute stage or high pain: prefer Low intensity
        - High fatigue: prefer Maintain or Regress
        - Otherwise: prefer Moderate/High with Progression
        """
        candidates = [
            i for i, p in enumerate(PRESCRIPTION_PROFILES) if abs(p[0] - stage) <= 1
        ]

        if pain > 0.7 or stage == 0:
            # Low intensity only
            preferred = [i for i in candidates if PRESCRIPTION_PROFILES[i][1] == "Low"]
        elif fatigue > 0.65:
            # Avoid High intensity
            preferred = [
                i
                for i in candidates
                if PRESCRIPTION_PROFILES[i][1] != "High"
                and PRESCRIPTION_PROFILES[i][2] != "Progress"
            ]
        else:
            # Progress-oriented
            preferred = [
                i
                for i in candidates
                if PRESCRIPTION_PROFILES[i][1] in ("Moderate", "High")
                and PRESCRIPTION_PROFILES[i][2] == "Progress"
            ]

        pool = preferred if preferred else candidates
        return int(self.rng.choice(pool))

    def _compute_reward(
        self,
        prev_pain: float,
        curr_pain: float,
        prev_rom: float,
        curr_rom: float,
        prev_str: float,
        curr_str: float,
        adherence: float,
        overtraining: bool,
        prescription_stage: int,
        curr_stage: int,
        intensity: str,
    ) -> Tuple[float, Dict]:
        """Mirror of RewardFunction.compute() in environment.py."""
        delta_pain = prev_pain - curr_pain  # positive = improvement
        delta_rom = curr_rom - prev_rom
        delta_str = curr_str - prev_str

        r_pain = float(np.clip(delta_pain * 3.0, -1.0, 1.0))
        r_rom = float(np.clip(delta_rom * 3.0, -1.0, 1.0))
        r_strength = float(np.clip(delta_str * 3.0, -1.0, 1.0))
        r_adherence = adherence

        safety_penalty = 0.0
        if overtraining:
            safety_penalty += 0.5
        if curr_pain > 0.8:
            safety_penalty += 0.3
        if prescription_stage > curr_stage + 1:
            safety_penalty += 0.4
        if intensity == "High" and curr_stage <= 1:
            safety_penalty += 0.3
        r_safety = -min(1.0, safety_penalty)

        reward = (
            self.W_PAIN * r_pain
            + self.W_ROM * r_rom
            + self.W_STRENGTH * r_strength
            + self.W_ADHERENCE * r_adherence
            + self.W_SAFETY * r_safety
        )
        reward = float(np.clip(reward, -1.0, 1.0))

        return reward, {
            "r_pain": round(r_pain, 3),
            "r_rom": round(r_rom, 3),
            "r_strength": round(r_strength, 3),
            "r_adherence": round(r_adherence, 3),
            "r_safety": round(r_safety, 3),
            "reward_total": round(reward, 3),
        }

    def _simulate_patient(
        self, patient_id: int, injury_type: Optional[str] = None
    ) -> List[SessionRecord]:
        """Simulate a full patient recovery trajectory."""
        if injury_type is None:
            injury_type = str(self.rng.choice(self.INJURY_TYPES))

        profile = INJURY_PROFILES[injury_type]

        # ── Initial conditions ───────────────────────────────────────────
        severity = float(self.rng.uniform(*profile["severity_range"]))

        pain = float(self.rng.uniform(*profile["initial_pain"])) * (
            0.7 + 0.3 * severity
        )
        rom = float(self.rng.uniform(*profile["initial_rom"])) * (1.3 - 0.3 * severity)
        strength = float(self.rng.uniform(*profile["initial_str"])) * (
            1.3 - 0.3 * severity
        )
        pain = float(np.clip(pain, 0.0, 1.0))
        rom = float(np.clip(rom, 0.0, 1.0))
        strength = float(np.clip(strength, 0.0, 1.0))

        mov_qual = float(np.clip((rom + strength) / 2.0 + self._noise(), 0.0, 1.0))
        fatigue = float(self.rng.uniform(0.20, 0.50))
        adherence = float(
            np.clip(self.rng.normal(profile["adherence_base"], 0.08), 0.4, 1.0)
        )
        stage = 0

        records: List[SessionRecord] = []

        for session in range(1, self.max_sessions + 1):
            days_since = int(self.rng.integers(1, 4))

            # ── Choose prescription ──────────────────────────────────────
            action_id = self._select_prescription(stage, pain, fatigue)
            presc = PRESCRIPTION_PROFILES[action_id]
            p_stage, intensity, progression, p_name = presc

            # ── Intensity & progression multipliers ──────────────────────
            int_mult = {"Low": 0.7, "Moderate": 1.0, "High": 1.4}[intensity]
            prog_mult = {"Regress": 0.6, "Maintain": 0.9, "Progress": 1.2}[progression]
            load = int_mult * prog_mult

            stage_gap = abs(p_stage - stage)
            mismatch_penalty = stage_gap * 0.05

            # ── Overtraining check ───────────────────────────────────────
            overtraining = bool(
                load > 1.3
                and pain > 0.5
                and self.rng.random() < profile["overtraining_sensitivity"] * 0.3
            )

            # ── Pain dynamics ─────────────────────────────────────────────
            prev_pain = pain
            if overtraining:
                pain_delta = 0.06 * load + self._noise()
            elif p_stage <= stage:
                base_decay = profile["pain_decay"]
                pain_delta = (
                    -base_decay * (1 - pain) * (2.0 - load * 0.5) + self._noise()
                )
            else:
                pain_delta = 0.03 * stage_gap + mismatch_penalty + self._noise()
            pain = float(np.clip(pain + pain_delta, 0.0, 1.0))

            # ── ROM dynamics ──────────────────────────────────────────────
            prev_rom = rom
            rom_rate = profile["rom_growth"]
            if p_stage > stage + 1:
                rom_rate *= 0.3
            rom_gain = rom_rate * min(1.0, load * 0.8) * (1.0 - rom)
            rom = float(np.clip(rom + rom_gain + self._noise(), 0.0, 1.0))

            # ── Strength dynamics ─────────────────────────────────────────
            prev_str = strength
            if intensity in ("Moderate", "High") and p_stage >= stage:
                str_gain = profile["str_growth"] * load * (1.0 - strength)
            else:
                str_gain = profile["str_growth"] * 0.4 * (1.0 - strength)
            strength = float(np.clip(strength + str_gain + self._noise(), 0.0, 1.0))

            # ── Movement quality ──────────────────────────────────────────
            mq_gain = 0.025 * (rom + strength) / 2.0 + self._noise(0.5)
            mov_qual = float(np.clip(mov_qual + mq_gain, 0.0, 1.0))

            # ── Fatigue ───────────────────────────────────────────────────
            fatigue_inc = 0.10 * load * (2.0 if overtraining else 1.0)
            recovery_rate = 0.15 * (days_since / 3.0)
            fatigue = float(
                np.clip(
                    fatigue + fatigue_inc - recovery_rate + self._noise(0.5), 0.0, 1.0
                )
            )

            # ── Adherence (dropout model) ─────────────────────────────────
            if self.rng.random() < profile["dropout_risk"] * 0.05:
                adherence = max(0.1, adherence - float(self.rng.uniform(0.05, 0.20)))
            pain_effect = -0.05 if pain > 0.6 else 0.02
            prog_effect = 0.03 if (rom - prev_rom) > 0.01 else 0.0
            adherence = float(
                np.clip(
                    adherence + pain_effect + prog_effect + self._noise(0.3), 0.1, 1.0
                )
            )

            # ── Stage progression ─────────────────────────────────────────
            composite = (rom + strength) / 2.0
            if stage < 4 and composite >= STAGE_THRESHOLDS[stage]:
                stage = min(4, stage + 1)

            # ── Reward ────────────────────────────────────────────────────
            reward, components = self._compute_reward(
                prev_pain,
                pain,
                prev_rom,
                rom,
                prev_str,
                strength,
                adherence,
                overtraining,
                p_stage,
                stage,
                intensity,
            )

            # ── Termination ───────────────────────────────────────────────
            recovered = composite >= self.recovery_threshold and stage == 4

            rec = SessionRecord(
                patient_id=patient_id,
                session_number=session,
                injury_type=injury_type,
                injury_severity=round(severity, 3),
                recovery_stage=stage,
                stage_name=self.STAGE_NAMES[stage],
                pain_level=round(pain, 3),
                pain_vas=round(pain * 10.0, 1),
                rom=round(rom, 3),
                rom_pct=round(rom * 100.0, 1),
                strength=round(strength, 3),
                strength_pct=round(strength * 100.0, 1),
                movement_quality=round(mov_qual, 3),
                fatigue=round(fatigue, 3),
                adherence=round(adherence, 3),
                adherence_pct=round(adherence * 100.0, 1),
                days_since_last=days_since,
                composite_score=round(composite, 3),
                prescription_id=action_id,
                prescription_name=p_name,
                prescription_stage=p_stage,
                intensity=intensity,
                progression=progression,
                r_pain=components["r_pain"],
                r_rom=components["r_rom"],
                r_strength=components["r_strength"],
                r_adherence=components["r_adherence"],
                r_safety=components["r_safety"],
                reward_total=components["reward_total"],
                overtraining=overtraining,
                recovered=recovered,
                delta_pain=round(prev_pain - pain, 3),
                delta_rom=round(rom - prev_rom, 3),
                delta_strength=round(strength - prev_str, 3),
            )
            records.append(rec)

            if recovered:
                break

        return records

    # ── Public API ─────────────────────────────────────────────────────────

    def generate_dataset(
        self,
        n_patients: int = 500,
        injury_distribution: Optional[Dict[str, float]] = None,
        verbose: bool = True,
    ) -> pd.DataFrame:
        """
        Generate a full dataset of patient trajectories.

        Parameters
        ----------
        n_patients : int
            Number of unique patients to simulate (default 500).
        injury_distribution : dict or None
            Optional dict mapping injury_type → fraction.
            If None, uses uniform distribution across all 12 injuries.
        verbose : bool
            Print progress updates.

        Returns
        -------
        pd.DataFrame with one row per rehabilitation session.
        Columns match the SessionRecord fields.
        """
        if injury_distribution is None:
            # Uniform — each injury equally represented
            injuries = [
                self.INJURY_TYPES[i % len(self.INJURY_TYPES)] for i in range(n_patients)
            ]
        else:
            # Weighted sampling
            injury_types = list(injury_distribution.keys())
            weights = np.array(list(injury_distribution.values()), dtype=float)
            weights /= weights.sum()
            injuries = list(self.rng.choice(injury_types, size=n_patients, p=weights))

        all_records: List[SessionRecord] = []

        for pid in range(n_patients):
            if verbose and pid % 100 == 0:
                print(f"  Generating patient {pid + 1}/{n_patients}...")
            records = self._simulate_patient(pid + 1, injury_type=injuries[pid])
            all_records.extend(records)

        df = pd.DataFrame([asdict(r) for r in all_records])
        if verbose:
            print(
                f"\n[OK] Generated {len(df):,} session records from {n_patients} patients."
            )
            print(
                f"  Recovery rate : {df.groupby('patient_id')['recovered'].any().mean() * 100:.1f}%"
            )
            print(f"  Avg sessions  : {df.groupby('patient_id').size().mean():.1f}")
            print(f"  Mean reward   : {df['reward_total'].mean():.3f}")
        return df

    def generate_balanced_dataset(
        self,
        n_per_injury: int = 50,
        verbose: bool = True,
    ) -> pd.DataFrame:
        """
        Generate exactly n_per_injury patients for each of the 12 injury types.
        Ensures balanced representation across all conditions.

        Parameters
        ----------
        n_per_injury : int
            Patients per injury type (default 50 → 600 total patients).
        """
        n_patients = n_per_injury * len(self.INJURY_TYPES)

        injuries_ordered = []
        for inj in self.INJURY_TYPES:
            injuries_ordered.extend([inj] * n_per_injury)
        self.rng.shuffle(injuries_ordered)

        all_records: List[SessionRecord] = []
        for pid, inj in enumerate(injuries_ordered):
            if verbose and pid % 100 == 0:
                print(f"  Generating patient {pid + 1}/{n_patients}...")
            records = self._simulate_patient(pid + 1, injury_type=inj)
            all_records.extend(records)

        df = pd.DataFrame([asdict(r) for r in all_records])
        if verbose:
            print(
                f"\n[OK] Balanced dataset: {len(df):,} sessions from {n_patients} patients."
            )
            print(f"  ({n_per_injury} patients x {len(self.INJURY_TYPES)} injuries)")
        return df

    def get_rl_arrays(
        self,
        n_patients: int = 500,
        val_frac: float = 0.15,
        test_frac: float = 0.15,
    ) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        """
        Generate dataset and return (X_train, X_val, X_test) state vectors.

        Each row is a 32-dim state vector matching PatientState.to_vector():
        [injury_type x12 | stage x5 | pain | rom | strength |
         mov_qual | fatigue | adherence | days_since_norm | session_norm |
         severity | joint_angles x6]

        Parameters
        ----------
        n_patients : int
        val_frac   : float  Validation fraction (default 0.15)
        test_frac  : float  Test fraction (default 0.15)

        Returns
        -------
        X_train, X_val, X_test : np.ndarray, shape (N, 32)
        """
        df = self.generate_dataset(n_patients=n_patients, verbose=False)
        X = self._df_to_state_vectors(df)

        n = len(X)
        n_val = int(n * val_frac)
        n_tst = int(n * test_frac)

        idx = self.rng.permutation(n)
        return X[idx[n_val + n_tst :]], X[idx[:n_val]], X[idx[n_val : n_val + n_tst]]

    def _df_to_state_vectors(self, df: pd.DataFrame) -> np.ndarray:
        """Convert DataFrame rows into 32-dim state vectors."""
        INJURY_TYPES = self.INJURY_TYPES
        vectors = []

        for _, row in df.iterrows():
            # Injury one-hot (12)
            inj_oh = np.zeros(12, dtype=np.float32)
            try:
                inj_oh[INJURY_TYPES.index(row["injury_type"])] = 1.0
            except ValueError:
                inj_oh[0] = 1.0

            # Stage one-hot (5)
            stage_oh = np.zeros(5, dtype=np.float32)
            stage_oh[int(np.clip(row["recovery_stage"], 0, 4))] = 1.0

            # Continuous metrics (9)
            cont = np.array(
                [
                    row["pain_level"],
                    row["rom"],
                    row["strength"],
                    row["movement_quality"],
                    row["fatigue"],
                    row["adherence"],
                    min(1.0, row["days_since_last"] / 14.0),
                    min(1.0, row["session_number"] / 50.0),
                    row["injury_severity"],
                ],
                dtype=np.float32,
            )

            # Joint angles (6) — zeroed in synthetic data
            joints = np.zeros(6, dtype=np.float32)

            vectors.append(np.concatenate([inj_oh, stage_oh, cont, joints]))

        return np.stack(vectors).astype(np.float32)

    def get_profile_statistics(self) -> pd.DataFrame:
        """
        Return a summary DataFrame of recovery profiles for all 12 injuries.
        Useful for understanding expected outcome distributions.
        """
        rows = []
        for name, p in INJURY_PROFILES.items():
            rows.append(
                {
                    "injury_type": name,
                    "initial_pain_lo": p["initial_pain"][0],
                    "initial_pain_hi": p["initial_pain"][1],
                    "initial_rom_lo": p["initial_rom"][0],
                    "initial_rom_hi": p["initial_rom"][1],
                    "initial_str_lo": p["initial_str"][0],
                    "initial_str_hi": p["initial_str"][1],
                    "recovery_weeks": p["recovery_weeks"],
                    "pain_decay_rate": p["pain_decay"],
                    "rom_growth_rate": p["rom_growth"],
                    "str_growth_rate": p["str_growth"],
                    "typical_adherence": p["adherence_base"],
                    "dropout_risk": p["dropout_risk"],
                    "overtraining_risk": p["overtraining_sensitivity"],
                    "clinical_notes": p["notes"],
                }
            )
        return pd.DataFrame(rows)

    def save_dataset(
        self,
        df: pd.DataFrame,
        output_dir: str = str(SYNTHETIC_DATA_DIR),
        prefix: str = "rehab_synthetic",
        formats: List[str] = ["csv", "json"],
    ) -> Dict[str, str]:
        """
        Save the dataset to disk.

        Parameters
        ----------
        df         : DataFrame from generate_dataset()
        output_dir : Directory to save files (default "data/")
        prefix     : Filename prefix (default "rehab_synthetic")
        formats    : List of formats: ["csv", "json", "npy"]

        Returns
        -------
        dict mapping format → saved file path
        """
        os.makedirs(output_dir, exist_ok=True)
        saved = {}

        if "csv" in formats:
            path = os.path.join(output_dir, f"{prefix}.csv")
            df.to_csv(path, index=False)
            saved["csv"] = path
            print(f"  [OK] CSV  -> {path}  ({len(df):,} rows)")

        if "json" in formats:
            path = os.path.join(output_dir, f"{prefix}.json")
            df.to_json(path, orient="records", indent=2)
            saved["json"] = path
            print(f"  [OK] JSON -> {path}")

        if "npy" in formats:
            X = self._df_to_state_vectors(df)
            path = os.path.join(output_dir, f"{prefix}_states.npy")
            np.save(path, X)
            saved["npy"] = path
            print(f"  [OK] NPY  -> {path}  shape={X.shape}")

        # Always save profile statistics
        prof_path = os.path.join(output_dir, f"{prefix}_profiles.csv")
        self.get_profile_statistics().to_csv(prof_path, index=False)
        saved["profiles"] = prof_path
        print(f"  [OK] Profiles -> {prof_path}")

        return saved

    def generate_and_save(
        self,
        n_patients: int = 500,
        output_dir: str = str(SYNTHETIC_DATA_DIR),
        balanced: bool = True,
        formats: List[str] = ["csv", "json", "npy"],
    ) -> Dict[str, str]:
        """
        One-call convenience method: generate + save everything.

        Parameters
        ----------
        n_patients : int  (used when balanced=False)
        output_dir : str
        balanced   : bool  If True, uses generate_balanced_dataset()
                          with n_patients//12 per injury (min 10)
        formats    : list

        Returns
        -------
        dict mapping format → saved file path
        """
        print("=" * 60)
        print("RehabRL Synthetic Data Generator")
        print("=" * 60)

        if balanced:
            n_per_inj = max(10, n_patients // len(self.INJURY_TYPES))
            print(f"Mode    : Balanced ({n_per_inj} per injury x 12 injuries)")
            df = self.generate_balanced_dataset(n_per_injury=n_per_inj)
        else:
            print(f"Mode    : Random   ({n_patients} patients, uniform injury)")
            df = self.generate_dataset(n_patients=n_patients)

        print(f"\nSaving to '{output_dir}/'...")
        return self.save_dataset(df, output_dir=output_dir, formats=formats)


# ── CLI entry point ────────────────────────────────────────────────────────────

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description="Generate synthetic rehabilitation patient dataset for RehabRL"
    )
    parser.add_argument(
        "--n-patients",
        type=int,
        default=600,
        help="Total number of patients (default: 600)",
    )
    parser.add_argument(
        "--output-dir",
        type=str,
        default=str(SYNTHETIC_DATA_DIR),
        help="Output directory",
    )
    parser.add_argument(
        "--balanced",
        action="store_true",
        default=True,
        help="Generate balanced dataset across all 12 injuries",
    )
    parser.add_argument(
        "--seed", type=int, default=42, help="Random seed (default: 42)"
    )
    parser.add_argument(
        "--formats",
        nargs="+",
        default=["csv", "json", "npy"],
        choices=["csv", "json", "npy"],
        help="Output formats (default: csv json npy)",
    )
    args = parser.parse_args()

    gen = RehabDataGenerator(seed=args.seed)
    saved = gen.generate_and_save(
        n_patients=args.n_patients,
        output_dir=args.output_dir,
        balanced=args.balanced,
        formats=args.formats,
    )

    print("\n" + "=" * 60)
    print("Summary of saved files:")
    for fmt, path in saved.items():
        print(f"  {fmt:10s}: {path}")
    print("=" * 60)
    print("\nDone! Load with:")
    print("  import pandas as pd")
    print(f"  df = pd.read_csv('{SYNTHETIC_DATA_DIR / 'rehab_synthetic.csv'}')")
    print("  print(df.head())")
