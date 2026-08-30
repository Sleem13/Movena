"""
rehab_rl/data/exercise_database.py
Exercise library and action prescription templates.
Each of the 30 discrete actions maps to a complete rehabilitation prescription.
"""

from dataclasses import dataclass, field
from typing import List, Optional
import numpy as np


# ─── Data structures ─────────────────────────────────────────────────────────


@dataclass
class Exercise:
    name: str
    category: str  # ROM | Strength | Proprioception | Cardio | Neuromuscular | Manual
    sets: int
    reps: str  # e.g. "10–12" or "30 sec"
    intensity: str  # Low | Moderate | High
    stage_min: int  # Earliest recovery stage (0-indexed)
    stage_max: int  # Latest recovery stage
    pain_limit: int  # Max acceptable pain level (0–10)
    description: str = ""
    cue: str = ""
    target_injuries: List[str] = field(init=False)
    role: str = field(init=False)

    def __post_init__(self):
        roles = {
            "ROM": "Physiopedia: Joint Mobility & Flexibility Restoration",
            "Strength": "Physiopedia: Progressive Tissue Loading",
            "Proprioception": "Physiopedia: Sensorimotor & Balance Retraining",
            "Cardio": "Physiopedia: Aerobic Capacity & Systemic Recovery",
            "Neuromuscular": "Physiopedia: Motor Control & Reactive Stability",
            "Manual": "Physiopedia: Passive Tissue Extensibility & Pain Modulation",
        }
        self.role = roles.get(self.category, "General Rehabilitation Protocol")

        db = {
            "Ankle Pumps": [
                "Ankle Sprain",
                "Achilles Tendinopathy",
                "Plantar Fasciitis",
            ],
            "Quad Sets": ["ACL Tear", "Patellofemoral Syndrome"],
            "Heel Slides": [
                "ACL Tear",
                "Patellofemoral Syndrome",
                "Hip Labral Tear",
                "Hamstring Strain",
            ],
            "SLR (Straight Leg Raise)": [
                "ACL Tear",
                "Patellofemoral Syndrome",
                "Hip Labral Tear",
                "Lumbar Disc Herniation",
            ],
            "Calf Raises (seated)": [
                "Ankle Sprain",
                "Achilles Tendinopathy",
                "Plantar Fasciitis",
            ],
            "Terminal Knee Extensions": ["ACL Tear", "Patellofemoral Syndrome"],
            "Mini Squats (0–45°)": [
                "ACL Tear",
                "Patellofemoral Syndrome",
                "Hip Labral Tear",
            ],
            "Standing Hip Abduction": [
                "Hip Labral Tear",
                "Patellofemoral Syndrome",
                "ACL Tear",
            ],
            "Hip Extension (prone)": [
                "Hip Labral Tear",
                "Hamstring Strain",
                "Lumbar Disc Herniation",
            ],
            "Single-Leg Balance": ["Ankle Sprain", "ACL Tear", "Achilles Tendinopathy"],
            "Step-Ups (low box)": [
                "ACL Tear",
                "Patellofemoral Syndrome",
                "Hip Labral Tear",
                "Ankle Sprain",
            ],
            "Clamshells": [
                "Hip Labral Tear",
                "Patellofemoral Syndrome",
                "Lumbar Disc Herniation",
            ],
            "Hamstring Curls (prone)": ["Hamstring Strain", "ACL Tear"],
            "Wall Slides": [
                "Rotator Cuff Tear",
                "Shoulder Impingement",
                "Cervical Strain",
            ],
            "Leg Press": [
                "ACL Tear",
                "Patellofemoral Syndrome",
                "Hip Labral Tear",
                "Hamstring Strain",
                "Ankle Sprain",
            ],
            "Romanian Deadlift": [
                "Hamstring Strain",
                "Lumbar Disc Herniation",
                "Hip Labral Tear",
            ],
            "Bulgarian Split Squat": [
                "ACL Tear",
                "Patellofemoral Syndrome",
                "Hip Labral Tear",
            ],
            "Lateral Band Walks": [
                "Hip Labral Tear",
                "Patellofemoral Syndrome",
                "ACL Tear",
                "Lumbar Disc Herniation",
            ],
            "Balance Board (eyes closed)": [
                "Ankle Sprain",
                "ACL Tear",
                "Achilles Tendinopathy",
            ],
            "Nordic Hamstring Curls": ["Hamstring Strain", "ACL Tear"],
            "Resistance Band Row": [
                "Rotator Cuff Tear",
                "Shoulder Impingement",
                "Cervical Strain",
                "Tennis Elbow",
            ],
            "Box Jumps (low)": [
                "ACL Tear",
                "Ankle Sprain",
                "Achilles Tendinopathy",
                "Patellofemoral Syndrome",
            ],
            "Single-Leg Squat": [
                "ACL Tear",
                "Patellofemoral Syndrome",
                "Hip Labral Tear",
            ],
            "Agility Ladder Drills": [
                "ACL Tear",
                "Ankle Sprain",
                "Achilles Tendinopathy",
                "Hamstring Strain",
            ],
            "Lateral Hops": ["ACL Tear", "Ankle Sprain", "Patellofemoral Syndrome"],
            "Trap Bar Deadlift": [
                "Hamstring Strain",
                "Lumbar Disc Herniation",
                "Hip Labral Tear",
                "ACL Tear",
            ],
            "Sled Push": [
                "ACL Tear",
                "Patellofemoral Syndrome",
                "Hamstring Strain",
                "Achilles Tendinopathy",
            ],
            "Band Pull-Aparts": [
                "Rotator Cuff Tear",
                "Shoulder Impingement",
                "Cervical Strain",
                "Tennis Elbow",
            ],
        }
        self.target_injuries = db.get(self.name, ["All"])


@dataclass
class Prescription:
    """A complete session prescription — one discrete action."""

    action_id: int
    name: str
    stage: int  # Target recovery stage (0–4)
    intensity: str  # Low | Moderate | High
    progression: str  # Regress | Maintain | Progress
    exercises: List[Exercise] = field(default_factory=list)
    frequency: str = "3×/week"
    duration: str = "45 min"
    rest: str = "60–90 sec"
    rationale: str = ""


# ─── Exercise Library (50+ exercises) ────────────────────────────────────────

EXERCISE_LIBRARY: List[Exercise] = [
    # ── Acute / Phase 0 ────────────────────────────────────────────────
    Exercise(
        "RICE Protocol",
        "Manual",
        1,
        "20 min",
        "Low",
        0,
        0,
        10,
        "Rest, Ice, Compression, Elevation.",
        "Ice for 15-20 min, elevate above heart level.",
    ),
    Exercise(
        "Passive ROM",
        "ROM",
        2,
        "10–15",
        "Low",
        0,
        1,
        6,
        "Therapist-guided joint mobilisation.",
        "Relax completely; let the therapist move the joint.",
    ),
    Exercise(
        "Ankle Pumps",
        "ROM",
        3,
        "20",
        "Low",
        0,
        1,
        8,
        "Dorsi/plantar flexion while seated.",
        "Pump slowly; full range without pain.",
    ),
    Exercise(
        "Quad Sets",
        "Strength",
        3,
        "10–15",
        "Low",
        0,
        1,
        7,
        "Isometric quad contraction in extension.",
        "Push knee flat into surface; hold 5 sec.",
    ),
    Exercise(
        "Heel Slides",
        "ROM",
        3,
        "10–15",
        "Low",
        0,
        1,
        7,
        "Supine knee flexion sliding heel toward glutes.",
        "Slide heel smoothly; stop at pain onset.",
    ),
    Exercise(
        "SLR (Straight Leg Raise)",
        "Strength",
        3,
        "10",
        "Low",
        0,
        2,
        6,
        "Supine hip flexion with knee in extension.",
        "Keep core braced; toes pulled back.",
    ),
    Exercise(
        "Calf Raises (seated)",
        "Strength",
        3,
        "15",
        "Low",
        0,
        2,
        7,
        "Plantar flexion seated for early loading.",
        "Slow and controlled, both up and down.",
    ),
    Exercise(
        "Deep Diaphragmatic Breathing",
        "Manual",
        2,
        "5 min",
        "Low",
        0,
        4,
        10,
        "Parasympathetic activation to reduce pain perception.",
        "Inhale 4 sec, hold 2 sec, exhale 6 sec.",
    ),
    # ── Subacute / Phase 1 ──────────────────────────────────────────────
    Exercise(
        "Terminal Knee Extensions",
        "Strength",
        3,
        "15",
        "Low",
        1,
        3,
        6,
        "Banded terminal knee extension for VMO activation.",
        "Straighten fully; squeeze at the top.",
    ),
    Exercise(
        "Mini Squats (0–45°)",
        "Strength",
        3,
        "12–15",
        "Low",
        1,
        3,
        5,
        "Partial squat within pain-free range.",
        "Keep knees over toes; chest up.",
    ),
    Exercise(
        "Standing Hip Abduction",
        "Strength",
        3,
        "12",
        "Low",
        1,
        3,
        6,
        "Side leg raises with band for hip stability.",
        "Maintain neutral pelvis; avoid trunk lean.",
    ),
    Exercise(
        "Hip Extension (prone)",
        "Strength",
        3,
        "12",
        "Low",
        1,
        3,
        6,
        "Prone hip extension to target glutes.",
        "Squeeze glute at top; no lumbar hyperextension.",
    ),
    Exercise(
        "Single-Leg Balance",
        "Proprioception",
        3,
        "30 sec",
        "Low",
        1,
        4,
        5,
        "Eyes-open unilateral stance on flat surface.",
        "Soft knee; focus point ahead; small adjustments OK.",
    ),
    Exercise(
        "Step-Ups (low box)",
        "Strength",
        3,
        "10",
        "Moderate",
        1,
        3,
        5,
        "Controlled step onto 15 cm box, lead with involved leg.",
        "Drive through heel; avoid knee valgus.",
    ),
    Exercise(
        "Stationary Bike",
        "Cardio",
        1,
        "15 min",
        "Low",
        1,
        4,
        5,
        "Low-resistance cycling for ROM and cardiovascular.",
        "Adjust seat so knee is slightly bent at bottom.",
    ),
    Exercise(
        "Clamshells",
        "Strength",
        3,
        "15",
        "Low",
        1,
        3,
        5,
        "Side-lying hip external rotation with band.",
        "Stack hips; rotate like a clamshell; hold 2 sec.",
    ),
    Exercise(
        "Hamstring Curls (prone)",
        "Strength",
        3,
        "12",
        "Low",
        1,
        3,
        5,
        "Prone knee flexion with light resistance.",
        "Control the lowering phase over 3 sec.",
    ),
    Exercise(
        "Wall Slides",
        "ROM",
        3,
        "15",
        "Low",
        1,
        3,
        6,
        "Shoulder ROM exercise along wall.",
        "Keep scapula retracted; no shrugging.",
    ),
    # ── Remodeling / Phase 2 ────────────────────────────────────────────
    Exercise(
        "Leg Press",
        "Strength",
        4,
        "10–12",
        "Moderate",
        2,
        4,
        4,
        "Progressive loading through full range.",
        "Control the eccentric; 3 sec down.",
    ),
    Exercise(
        "Romanian Deadlift",
        "Strength",
        4,
        "8–10",
        "Moderate",
        2,
        4,
        4,
        "Hip hinge pattern for posterior chain.",
        "Hinge at hips; bar stays close to legs.",
    ),
    Exercise(
        "Bulgarian Split Squat",
        "Strength",
        3,
        "8–10",
        "Moderate",
        2,
        4,
        4,
        "Unilateral loading to address strength asymmetry.",
        "90/90 at both knees; drive through front heel.",
    ),
    Exercise(
        "Lateral Band Walks",
        "Neuromuscular",
        3,
        "15 ea",
        "Moderate",
        2,
        4,
        4,
        "Hip abductor activation with band for frontal stability.",
        "Slight squat; maintain tension throughout.",
    ),
    Exercise(
        "Balance Board (eyes closed)",
        "Proprioception",
        3,
        "45 sec",
        "Moderate",
        2,
        4,
        3,
        "Advanced proprioceptive challenge on unstable surface.",
        "Eyes closed; arms at sides; adjust with ankle strategy.",
    ),
    Exercise(
        "Nordic Hamstring Curls",
        "Strength",
        3,
        "6–8",
        "High",
        2,
        4,
        3,
        "Eccentric hamstring loading for injury prevention.",
        "Lower body as slowly as possible; catch with arms.",
    ),
    Exercise(
        "Resistance Band Row",
        "Strength",
        3,
        "12–15",
        "Moderate",
        2,
        4,
        4,
        "Horizontal pull for scapular stability.",
        "Retract scapula fully; hold 1 sec.",
    ),
    Exercise(
        "Treadmill Jogging",
        "Cardio",
        1,
        "20 min",
        "Moderate",
        2,
        4,
        4,
        "Progressive running reintroduction at controlled pace.",
        "Comfortable talking pace; watch for antalgic gait.",
    ),
    # ── Functional / Phase 3 ────────────────────────────────────────────
    Exercise(
        "Box Jumps (low)",
        "Neuromuscular",
        3,
        "6",
        "High",
        3,
        4,
        3,
        "Bilateral plyometric for power development.",
        "Land softly with hips/knees/ankles bent; absorb force.",
    ),
    Exercise(
        "Single-Leg Squat",
        "Strength",
        4,
        "8–10",
        "High",
        3,
        4,
        2,
        "Advanced unilateral strength and neuromuscular control.",
        "Keep knee aligned over 2nd toe; slow and controlled.",
    ),
    Exercise(
        "Agility Ladder Drills",
        "Neuromuscular",
        3,
        "4 sets",
        "High",
        3,
        4,
        2,
        "Footwork patterns for dynamic neuromuscular control.",
        "Light on feet; precise foot placement each rung.",
    ),
    Exercise(
        "Lateral Hops",
        "Proprioception",
        3,
        "10 ea",
        "High",
        3,
        4,
        2,
        "Side-to-side single-leg bounding for frontal plane power.",
        "Stick each landing 2 sec before next hop.",
    ),
    Exercise(
        "Trap Bar Deadlift",
        "Strength",
        4,
        "5–6",
        "High",
        3,
        4,
        2,
        "High-load hip hinge for maximal strength.",
        "Full breath; brace core; drive floor away.",
    ),
    Exercise(
        "Farmer's Carry",
        "Strength",
        3,
        "30 m",
        "Moderate",
        3,
        4,
        3,
        "Loaded carry for functional stability.",
        "Tall posture; grip firmly; controlled gait.",
    ),
    Exercise(
        "Sled Push",
        "Cardio",
        3,
        "20 m",
        "High",
        3,
        4,
        2,
        "Loaded pushing for athletic conditioning.",
        "Lean into sled; drive with legs and hips.",
    ),
    Exercise(
        "Band Pull-Aparts",
        "Strength",
        3,
        "20",
        "Low",
        1,
        4,
        6,
        "Scapular retractors and horizontal abductors.",
        "Arms straight; pull band apart to chest height.",
    ),
    # ── Return to Activity / Phase 4 ────────────────────────────────────
    Exercise(
        "Sport-Specific Drills",
        "Neuromuscular",
        4,
        "10 min",
        "High",
        4,
        4,
        1,
        "Movements mimicking the patient's target activity.",
        "Build confidence; simulate match/work conditions.",
    ),
    Exercise(
        "Interval Sprinting",
        "Cardio",
        5,
        "6×30 sec",
        "High",
        4,
        4,
        1,
        "High-intensity intervals for cardiovascular readiness.",
        "Full effort on sprint; full recovery between.",
    ),
    Exercise(
        "Plyometric Circuit",
        "Neuromuscular",
        3,
        "8 min",
        "High",
        4,
        4,
        1,
        "Explosive movement circuit: jumps, bounds, hops.",
        "Quality over quantity; rest if form degrades.",
    ),
    Exercise(
        "Power Cleans (light)",
        "Strength",
        4,
        "4–5",
        "High",
        4,
        4,
        1,
        "Olympic lifting for rapid force development.",
        "Fast hips; full extension; catch in power position.",
    ),
    Exercise(
        "Maintenance Strength",
        "Strength",
        3,
        "10–12",
        "Moderate",
        4,
        4,
        2,
        "Full-body resistance training for maintenance.",
        "Compound movements; progressive overload principle.",
    ),
    Exercise(
        "Mobilization / Mobility Flow",
        "ROM",
        1,
        "30 min",
        "Low",
        0,
        4,
        8,
        "Full-body mobility work for recovery and flexibility.",
        "Hold each position 30–60 sec; breathe into the stretch.",
    ),
    Exercise(
        "Foam Rolling",
        "Manual",
        1,
        "10 min",
        "Low",
        0,
        4,
        9,
        "Self-myofascial release for recovery.",
        "Slow rolling; pause 30 sec on tender spots.",
    ),
]


# ─── 30 Discrete Prescription Templates ──────────────────────────────────────


def _get_exercises_by_stage_intensity(
    stage: int, intensity: str, injury_type: Optional[str] = None
) -> List[Exercise]:
    """Select appropriate exercises for a given stage and intensity, prioritizing injury-specific ones."""
    pool = [e for e in EXERCISE_LIBRARY if e.stage_min <= stage <= e.stage_max]

    if intensity == "Low":
        pool = [e for e in pool if e.intensity == "Low"]
    elif intensity == "Moderate":
        pool = [e for e in pool if e.intensity in ("Low", "Moderate")]
    else:  # High
        pool = pool  # all

    # Always include foam rolling/mobilization as warm-up/cool-down
    warm_cool = [
        e for e in pool if e.name in ("Foam Rolling", "Mobilization / Mobility Flow")
    ]
    core_pool = [e for e in pool if e not in warm_cool]

    # Prioritize injury specific
    if injury_type:
        injury_specific = [e for e in core_pool if injury_type in e.target_injuries]
        general = [e for e in core_pool if "All" in e.target_injuries]
        other = [e for e in core_pool if e not in injury_specific and e not in general]
        core_exs = injury_specific + general + other
    else:
        core_exs = core_pool

    n_core = {0: 3, 1: 4, 2: 5}[min(2, stage // 2)]

    selected = []
    # Add warm up
    flow = [e for e in warm_cool if e.name == "Mobilization / Mobility Flow"]
    if flow:
        selected.append(flow[0])

    # Add core exercises
    selected.extend(core_exs[:n_core])

    # Add cool down
    roll = [e for e in warm_cool if e.name == "Foam Rolling"]
    if roll:
        selected.append(roll[0])

    return selected


def build_action_space() -> List[Prescription]:
    """
    Build 30 discrete prescriptions:
    5 recovery stages × 6 intensity/progression combinations.
    """
    intensity_prog = [
        ("Low", "Regress"),
        ("Low", "Maintain"),
        ("Moderate", "Maintain"),
        ("Moderate", "Progress"),
        ("High", "Maintain"),
        ("High", "Progress"),
    ]

    stage_meta = [
        ("Acute", "2–3×/week", "30–40 min", "90–120 sec"),
        ("Subacute", "3×/week", "40–50 min", "60–90 sec"),
        ("Remodeling", "3–4×/week", "50–60 min", "60–90 sec"),
        ("Functional", "4×/week", "60 min", "45–60 sec"),
        ("Return", "5×/week", "60–75 min", "30–45 sec"),
    ]

    prescriptions = []
    action_id = 0
    for stage_idx, (stage_name, freq, dur, rest) in enumerate(stage_meta):
        for intensity, progression in intensity_prog:
            exs = _get_exercises_by_stage_intensity(stage_idx, intensity)
            name = f"{stage_name} — {intensity} Intensity ({progression})"
            rationale = (
                f"Stage {stage_idx} ({stage_name}) prescription at {intensity.lower()} intensity. "
                f"RL policy chose to {progression.lower()} load based on current patient metrics."
            )
            p = Prescription(
                action_id=action_id,
                name=name,
                stage=stage_idx,
                intensity=intensity,
                progression=progression,
                exercises=exs,
                frequency=freq,
                duration=dur,
                rest=rest,
                rationale=rationale,
            )
            prescriptions.append(p)
            action_id += 1

    return prescriptions


# Singleton action space
ACTION_SPACE: List[Prescription] = build_action_space()


def get_prescription(action_id: int, injury_type: Optional[str] = None) -> Prescription:
    import copy

    p = copy.deepcopy(ACTION_SPACE[action_id])
    if injury_type:
        p.exercises = _get_exercises_by_stage_intensity(
            p.stage, p.intensity, injury_type
        )
    return p


def get_stage_actions(stage: int) -> List[int]:
    """Return action IDs valid for a given recovery stage."""
    return [p.action_id for p in ACTION_SPACE if p.stage == stage]


def action_to_vector(action_id: int) -> np.ndarray:
    """Encode prescription as a feature vector for logging/analysis."""
    p = ACTION_SPACE[action_id]
    intensity_map = {"Low": 0, "Moderate": 1, "High": 2}
    prog_map = {"Regress": -1, "Maintain": 0, "Progress": 1}
    return np.array(
        [
            p.stage / 4.0,
            intensity_map[p.intensity] / 2.0,
            (prog_map[p.progression] + 1) / 2.0,
            len(p.exercises) / 8.0,
        ],
        dtype=np.float32,
    )
