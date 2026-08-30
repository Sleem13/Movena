"""Clinician-facing rehabilitation protocol reference catalog.

This module deliberately does not change the RehabRL state/action dimensions.
Only conditions with ``rl_injury_type`` may be sent to the trained policy. The
remaining entries are evidence-informed protocol references for clinician review.
They are not diagnoses or autonomous treatment plans.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any


@dataclass(frozen=True)
class ProtocolPhase:
    stage: int
    name: str
    typical_timing: str
    goals: tuple[str, ...]
    interventions: tuple[str, ...]
    progression_criteria: tuple[str, ...]


@dataclass(frozen=True)
class ConditionProtocol:
    id: str
    name: str
    aliases: tuple[str, ...]
    category: str
    body_region: str
    summary: str
    outcome_measures: tuple[str, ...]
    red_flags: tuple[str, ...]
    precautions: tuple[str, ...]
    phases: tuple[ProtocolPhase, ...]
    sources: tuple[tuple[str, str], ...]
    rl_injury_type: str | None = None
    clinical_status: str = "clinician-review-required"
    evidence_reviewed_on: str = "2026-08-30"
    next_review_due: str = "2027-08-30"

    def to_dict(self, *, detail: bool = True) -> dict[str, Any]:
        value = asdict(self)
        value["rl_supported"] = self.rl_injury_type is not None
        value["search_text"] = " ".join(
            (self.name, *self.aliases, self.category, self.body_region)
        )
        value["sources"] = [
            {"title": title, "url": url} for title, url in self.sources
        ]
        if not detail:
            value.pop("phases")
            value.pop("red_flags")
            value.pop("precautions")
            value.pop("outcome_measures")
            value.pop("sources")
        return value


UNIVERSAL_RED_FLAGS = (
    "New chest pain, severe shortness of breath, syncope, or unstable vital signs",
    "Suspected fracture/dislocation, hot swollen joint, wound infection, or systemic illness",
    "New or rapidly progressive neurological deficit; bowel/bladder change or saddle anesthesia",
    "Possible deep-vein thrombosis: unexplained unilateral calf swelling, warmth, or tenderness",
    "Severe, unremitting, non-mechanical pain or unexplained constitutional symptoms",
)

ORTHO_SOURCE = (
    "APTA Orthopaedic Clinical Practice Guidelines",
    "https://www.orthopt.org/content/practice/clinical-practice-guidelines/cpgs",
)
ACL_SOURCE = (
    "AAOS ACL Injuries Clinical Practice Guideline",
    "https://www.aaos.org/aaos-home/newsroom/press-releases/aaos-updates-guideline-for-management-of-acl-injuries/",
)
ROTATOR_SOURCE = (
    "AAOS Management of Rotator Cuff Injuries (2025)",
    "https://www.aaos.org/quality/quality-programs/rotator-cuff/",
)
ANKLE_SOURCE = (
    "APTA Lateral Ankle Ligament Sprains (2021)",
    "https://www.orthopt.org/content/s/ankle-stability-and-movement-coordination-impairments-lateral-ankle-ligament-sprains-revision-2021",
)
PLANTAR_SOURCE = (
    "APTA Heel Pain—Plantar Fasciitis (2023)",
    "https://www.orthopt.org/content/s/heel-pain-plantar-fasciitis-revision-2023",
)
LOW_BACK_SOURCE = (
    "APTA Interventions for Acute and Chronic Low Back Pain (2021)",
    "https://www.orthopt.org/content/s/interventions-for-the-management-of-acute-and-chronic-low-back-pain-revision-2021",
)
HIP_OA_SOURCE = (
    "APTA Hip Pain and Mobility Deficits—Hip Osteoarthritis (2025)",
    "https://www.orthopt.org/content/publications/pub-cpg/hip-pain-and-mobility-deficits-hip-osteoarthritis-revision-2025",
)
MENISCUS_SOURCE = (
    "APTA Meniscal and Articular Cartilage Lesions (2018)",
    "https://www.orthopt.org/content/s/knee-pain-and-mobility-impairments-meniscal-and-articular-cartilage-lesions-2018",
)
STROKE_SOURCE = (
    "Canadian Stroke Best Practices—Rehabilitation Delivery",
    "https://www.strokebestpractices.ca/recommendations/stroke-rehabilitation-delivery",
)
PARKINSON_SOURCE = (
    "Parkinson's Foundation Exercise Guidelines",
    "https://www.parkinson.org/sites/default/files/documents/Parkinsons-Exercise-Guidelines-1025.pdf",
)
VESTIBULAR_SOURCE = (
    "ANPT Peripheral Vestibular Hypofunction CPG (2022)",
    "https://www.neuropt.org/docs/default-source/cpgs/vestibular-update/vestibular-hypofunction-cpg-revision-2021.pdf",
)
FALLS_SOURCE = (
    "APTA Physical Therapy Management of Fall Risk (2025)",
    "https://www.apta.org/patient-care/evidence-based-practice-resources/cpgs/physical-therapy-management-of-fall-risk-in-community-dwelling-older-adults",
)
OSTEOPOROSIS_SOURCE = (
    "APTA Physical Therapist Management of Osteoporosis (2022)",
    "https://www.apta.org/patient-care/evidence-based-practice-resources/cpgs/osteoporosis",
)


def _phase(
    stage: int,
    name: str,
    timing: str,
    goals: tuple[str, ...],
    interventions: tuple[str, ...],
    criteria: tuple[str, ...],
) -> ProtocolPhase:
    return ProtocolPhase(stage, name, timing, goals, interventions, criteria)


def _tissue_phases(
    early: tuple[str, ...],
    loading: tuple[str, ...],
    function: tuple[str, ...],
    *,
    return_goal: str = "Meet patient-specific work, recreation, or sport demands",
) -> tuple[ProtocolPhase, ...]:
    return (
        _phase(0, "Protection and symptom control", "Irritability-led; often days to 2 weeks",
               ("Exclude urgent pathology", "Settle reactive symptoms", "Maintain safe adjacent mobility"),
               early,
               ("Symptoms stable or improving over 24 hours", "Safe independent self-management", "No emerging red flags")),
        _phase(1, "Restore mobility and baseline control", "Criteria-led; commonly weeks 1–6",
               ("Restore usable range", "Normalize basic movement", "Begin tolerable loading"),
               (*early, *loading[:2]),
               ("Daily activities tolerated without sustained flare", "Improving range and motor control", "Load response acceptable by next day")),
        _phase(2, "Progressive capacity", "Criteria-led; commonly weeks 4–12+",
               ("Build strength and endurance", "Address kinetic-chain contributors", "Increase task exposure"),
               loading,
               ("Meaningful outcome-measure improvement", "Progressive resistance tolerated", "Movement quality maintained under fatigue")),
        _phase(3, "Functional integration", "When capacity supports task practice",
               ("Restore task-specific power, balance, and confidence", return_goal),
               function,
               ("Task testing near patient-specific target", "No instability or material symptom escalation", "Independent load management")),
        _phase(4, "Return and prevention", "After objective and shared-decision criteria are met",
               (return_goal, "Reduce recurrence risk", "Maintain long-term physical activity"),
               (*function, "Maintenance strength, conditioning, and self-monitoring plan"),
               ("Condition-specific functional testing passed", "Patient confidence and contextual risks reviewed", "Clinician clearance; surgeon clearance when applicable")),
    )


def _protocol(
    id: str,
    name: str,
    aliases: tuple[str, ...],
    category: str,
    region: str,
    summary: str,
    outcomes: tuple[str, ...],
    precautions: tuple[str, ...],
    phases: tuple[ProtocolPhase, ...],
    sources: tuple[tuple[str, str], ...],
    *,
    rl: str | None = None,
    red_flags: tuple[str, ...] = (),
) -> ConditionProtocol:
    return ConditionProtocol(
        id, name, aliases, category, region, summary, outcomes,
        (*UNIVERSAL_RED_FLAGS, *red_flags), precautions, phases, sources, rl,
    )


CATALOG: tuple[ConditionProtocol, ...] = (
    _protocol(
        "acl_tear", "Anterior cruciate ligament injury", ("ACL tear", "ACL reconstruction", "ACLR"),
        "Knee", "Lower limb", "Criteria-based rehabilitation after ACL injury or reconstruction; graft, concomitant injury, and surgeon restrictions govern loading.",
        ("IKDC or KOOS", "Effusion and range of motion", "Quadriceps strength symmetry", "Hop-test battery", "Movement quality and psychological readiness"),
        ("Follow graft-specific and concomitant meniscus/cartilage restrictions", "Do not use time alone for running or return-to-sport clearance"),
        _tissue_phases(
            ("Education, swelling control, extension restoration, quadriceps activation, gait retraining", "Patellar mobility and flexion within procedure restrictions"),
            ("Progressive quadriceps/hip/calf resistance", "Neuromuscular and single-leg control", "Graded running only after objective criteria"),
            ("Change-of-direction, landing, plyometric and sport/work exposure", "Objective strength, hop, movement-quality, and readiness testing"),
            return_goal="Return to required activity with shared, criteria-based risk review",
        ), (ACL_SOURCE, ORTHO_SOURCE), rl="ACL Tear",
        red_flags=("Locked knee, recurrent giving-way with injury, or marked acute effusion requires reassessment",),
    ),
    _protocol(
        "rotator_cuff_tear", "Rotator cuff tear", ("RC tear", "rotator cuff repair", "supraspinatus tear"),
        "Shoulder", "Upper limb", "Nonoperative or postoperative care based on tear characteristics, functional goals, irritability, and surgical restrictions.",
        ("SPADI or QuickDASH", "Pain-free active range", "External-rotation and elevation strength", "Task-specific reach/lift tolerance"),
        ("After repair, sling, passive motion, active motion, and resistance timing must follow the surgeon", "Avoid painful high-load elevation early"),
        _tissue_phases(
            ("Education and activity modification", "Supported or passive/active-assisted mobility as permitted", "Scapular and distal-limb movement"),
            ("Progressive rotator-cuff and scapular loading", "Mobility for identified deficits", "Graded elevation and closed-chain control"),
            ("Overhead endurance, lifting, perturbation, and work/sport simulation", "Strength and task testing"),
        ), (ROTATOR_SOURCE, ORTHO_SOURCE), rl="Rotator Cuff Tear",
    ),
    _protocol(
        "lumbar_radiculopathy", "Lumbar disc herniation with radicular pain", ("sciatica", "lumbar radiculopathy", "slipped disc"),
        "Spine", "Trunk", "Classification-informed management emphasizing neurological monitoring, directional preference when present, activity, and graded capacity.",
        ("Oswestry Disability Index", "Patient-Specific Functional Scale", "Pain distribution", "Neurological screen", "Walking/sitting tolerance"),
        ("Repeated movement is used only when it centralizes or improves symptoms", "Avoid prescribing flexion or extension by diagnosis label alone"),
        _tissue_phases(
            ("Education to remain active within tolerance", "Positions/movements that centralize symptoms", "Frequent short walks"),
            ("Trunk coordination and graded mobility", "Neural mobility when indicated and non-provocative", "Progressive aerobic activity"),
            ("Progressive lifting, carrying, endurance, and work exposure", "Self-management and recurrence planning"),
        ), (LOW_BACK_SOURCE, ORTHO_SOURCE), rl="Lumbar Disc Herniation",
        red_flags=("Progressive motor loss, saddle anesthesia, or bowel/bladder dysfunction requires emergency assessment",),
    ),
    _protocol(
        "lateral_ankle_sprain", "Lateral ankle sprain", ("ankle sprain", "rolled ankle", "chronic ankle instability"),
        "Foot and ankle", "Lower limb", "Early protected loading followed by range, strength, balance, and graded hopping/change-of-direction exposure.",
        ("LEFS or FAAM", "Weight-bearing dorsiflexion", "Single-leg balance", "Star Excursion/Y-Balance", "Hop and change-of-direction tests"),
        ("Use fracture decision rules and medical imaging referral when indicated", "Brace/tape may support activity but does not replace rehabilitation"),
        _tissue_phases(
            ("Protection/compression and optimal loading", "Pain-limited range and gait retraining", "External support when indicated"),
            ("Calf/peroneal strength and dorsiflexion mobility", "Static-to-dynamic balance", "Progressive walking and stairs"),
            ("Hopping, landing, acceleration, cutting, and sport/work drills", "Recurrence-prevention balance and strength program"),
        ), (ANKLE_SOURCE,), rl="Ankle Sprain",
    ),
    _protocol(
        "lateral_elbow_tendinopathy", "Lateral elbow tendinopathy", ("tennis elbow", "lateral epicondylalgia", "common extensor tendinopathy"),
        "Elbow", "Upper limb", "Graded wrist-extensor and upper-limb loading with ergonomic and activity modification based on 24-hour response.",
        ("PRTEE", "Grip strength", "Pain-free grip", "Patient-Specific Functional Scale"),
        ("Screen cervical/radial nerve contribution and intra-articular pathology", "Avoid repeated high-irritability gripping without load modification"),
        _tissue_phases(("Relative load reduction and education", "Pain-modulating isometrics when helpful"),
                       ("Progressive wrist extensor/flexor and grip resistance", "Shoulder/scapular conditioning", "Graded occupational or racquet loading"),
                       ("High-speed grip, lifting, racquet or work simulation", "Long-term load-management plan")),
        (ORTHO_SOURCE,), rl="Tennis Elbow",
    ),
    _protocol(
        "patellofemoral_pain", "Patellofemoral pain", ("PFP", "runner's knee", "anterior knee pain", "patellofemoral syndrome"),
        "Knee", "Lower limb", "Education and combined hip/knee exercise with temporary load modification; adjuncts are impairment- and response-based.",
        ("Kujala/AKPS", "Anterior Knee Pain Scale", "Step-down or single-leg squat", "Training-load tolerance"),
        ("Screen for effusion, locking, instability, referred hip/spine pain, and growth-related pathology", "Pain response and next-day recovery guide load"),
        _tissue_phases(("Reduce provocative training dose while maintaining activity", "Taping or foot orthosis trial when clinically indicated"),
                       ("Progressive quadriceps and posterolateral hip strength", "Movement retraining and graded running/stairs"),
                       ("Single-leg strength, hopping, running and sport exposure", "Training-load and recurrence plan")),
        (ORTHO_SOURCE,), rl="Patellofemoral Syndrome",
    ),
    _protocol(
        "nonarthritic_hip_pain", "Nonarthritic hip joint pain", ("hip labral tear", "FAI", "femoroacetabular impingement", "hip-related groin pain"),
        "Hip", "Lower limb", "Impairment-based hip and trunk rehabilitation with activity modification and graded return; imaging findings require clinical correlation.",
        ("iHOT-12 or HAGOS", "Hip Outcome Score", "Hip range and strength", "Single-leg task tolerance"),
        ("Avoid repeatedly forcing symptomatic impingement positions", "Mechanical locking or inability to bear weight needs medical review"),
        _tissue_phases(("Education and modification of compressive positions", "Comfortable hip mobility and trunk control"),
                       ("Hip and trunk progressive resistance", "Single-leg control and graded squat/hinge", "Aerobic conditioning"),
                       ("Cutting, running, lifting and sport/work exposure", "Patient-specific strength and functional tests")),
        (ORTHO_SOURCE,), rl="Hip Labral Tear",
    ),
    _protocol(
        "achilles_tendinopathy", "Achilles tendinopathy", ("Achilles tendon pain", "midportion Achilles", "insertional Achilles"),
        "Foot and ankle", "Lower limb", "Progressive tendon loading and activity management; insertional symptoms may require modified dorsiflexion range.",
        ("VISA-A", "Single-leg heel-rise endurance", "Pain-monitoring response", "Hop/running tolerance"),
        ("Suspected acute rupture requires urgent assessment", "Avoid compressive end-range dorsiflexion early for insertional disease"),
        _tissue_phases(("Education and temporary reduction of high-strain activity", "Tolerable calf isometrics or bilateral raises"),
                       ("Progressive seated and standing calf resistance", "Heavy-slow or eccentric-concentric loading", "Graded running exposure"),
                       ("Energy-storage hopping, running and sport drills", "Long-term calf loading and workload plan")),
        (ORTHO_SOURCE,), rl="Achilles Tendinopathy",
    ),
    _protocol(
        "rotator_cuff_related_pain", "Rotator cuff–related shoulder pain", ("shoulder impingement", "subacromial pain", "RCRSP"),
        "Shoulder", "Upper limb", "Active rehabilitation centered on graded cuff/scapular loading, mobility when limited, and task-specific exposure.",
        ("SPADI", "QuickDASH", "Active elevation", "External-rotation strength", "Work/overhead tolerance"),
        ("Acute traumatic weakness, dislocation, or suspected full-thickness tear needs reassessment", "Do not force painful arc repeatedly"),
        _tissue_phases(("Education, sleep/activity modification, comfortable motion", "Low-load cuff and scapular activation"),
                       ("Progressive cuff/scapular resistance", "Thoracic/shoulder mobility for measured deficits", "Graded overhead exposure"),
                       ("Overhead endurance, power, carrying and sport/work drills", "Independent maintenance plan")),
        (ROTATOR_SOURCE, ORTHO_SOURCE), rl="Shoulder Impingement",
    ),
    _protocol(
        "plantar_heel_pain", "Plantar heel pain", ("plantar fasciitis", "plantar fasciopathy", "heel spur pain"),
        "Foot and ankle", "Lower limb", "Education, plantar fascia/calf stretching, foot/ankle resistance, and graded weight-bearing; taping/orthoses are adjuncts.",
        ("FAAM or FFI", "First-step pain", "Foot/ankle strength", "Walking/standing tolerance"),
        ("Screen for calcaneal stress injury, fat-pad disorder, and neural pain", "Night splints are considered mainly when first-step pain persists"),
        _tissue_phases(("Load and footwear education", "Plantar fascia-specific and calf stretching", "Taping trial when appropriate"),
                       ("Progressive foot intrinsic and calf resistance", "Graded walking and standing", "Orthosis trial when indicated"),
                       ("Running/jumping progression and work conditioning", "Footwear and maintenance-loading plan")),
        (PLANTAR_SOURCE,), rl="Plantar Fasciitis",
    ),
    _protocol(
        "mechanical_neck_pain", "Mechanical neck pain", ("cervical strain", "neck pain", "whiplash-associated disorder"),
        "Spine", "Upper quarter", "Classification-informed mobility, motor-control, endurance, education, and activity restoration.",
        ("Neck Disability Index", "Patient-Specific Functional Scale", "Cervical range", "Deep-neck-flexor endurance"),
        ("Screen trauma, vascular symptoms, myelopathy, radiculopathy, and concussion", "Manual therapy is an adjunct to active care"),
        _tissue_phases(("Education, comfortable movement, sleep/work modification", "Gentle cervical/scapular motor control"),
                       ("Cervical and scapulothoracic endurance/strength", "Mobility or manual therapy for measured deficits", "Graded aerobic activity"),
                       ("Work, driving, lifting and sport exposure", "Self-management and conditioning")),
        (ORTHO_SOURCE,), rl="Cervical Strain",
        red_flags=("Signs of cervical myelopathy or vascular compromise require urgent medical assessment",),
    ),
    _protocol(
        "hamstring_strain", "Hamstring strain injury", ("pulled hamstring", "hamstring tear", "posterior thigh strain"),
        "Hip and thigh", "Lower limb", "Progressive lengthened-state strength, running exposure, lumbopelvic control, and sport-specific return criteria.",
        ("Pain and palpation length", "Knee-flexor strength", "Askling H-test when appropriate", "High-speed running tolerance"),
        ("Large hematoma, palpable defect, marked weakness, or proximal avulsion signs require imaging/medical review", "Avoid premature high-speed running"),
        _tissue_phases(("Relative protection, pain-limited gait and range", "Early low-load isometrics"),
                       ("Progressive eccentric and lengthened-state hamstring resistance", "Lumbopelvic and kinetic-chain training", "Graded running from submaximal to faster exposures"),
                       ("Max-velocity running, acceleration/deceleration and sport drills", "Strength, sprint exposure and apprehension testing")),
        (ORTHO_SOURCE,), rl="Hamstring Strain",
    ),
    _protocol(
        "knee_osteoarthritis", "Knee osteoarthritis", ("knee OA", "degenerative knee arthritis"),
        "Knee", "Lower limb", "Long-term exercise, education, weight-management support when relevant, and functional strengthening tailored to symptoms and goals.",
        ("KOOS or WOMAC", "30-second chair stand", "Timed Up and Go", "Walking tolerance", "Gait speed"),
        ("Acute hot swollen joint, true locking, or rapid deterioration needs medical review", "Dose around irritability while preserving regular activity"),
        _tissue_phases(("Education, flare plan, comfortable range and low-impact aerobic activity",),
                       ("Progressive quadriceps/hip/calf resistance", "Balance and gait training", "Aerobic conditioning and functional practice"),
                       ("Stairs, sit-to-stand, carrying and community mobility", "Sustainable weekly strength/aerobic plan")),
        (ORTHO_SOURCE,),
    ),
    _protocol(
        "hip_osteoarthritis", "Hip osteoarthritis", ("hip OA", "degenerative hip arthritis"),
        "Hip", "Lower limb", "Education, individualized exercise, gait/balance training, and manual therapy when indicated, integrated with long-term activity.",
        ("WOMAC or HOOS", "30-second chair stand", "Timed Up and Go", "Timed stairs", "Walking tolerance"),
        ("Sudden inability to weight-bear or suspected fracture requires urgent review", "Respect postoperative precautions if arthroplasty has occurred"),
        _tissue_phases(("Education, symptom-guided mobility, walking aid assessment",),
                       ("Hip and lower-limb progressive resistance", "Balance/gait training", "Aerobic conditioning", "Manual therapy for selected mobility deficits"),
                       ("Stairs, transfers, carrying and community walking", "Sustainable strength and aerobic plan")),
        (HIP_OA_SOURCE,),
    ),
    _protocol(
        "meniscal_injury", "Meniscal or articular cartilage lesion", ("meniscus tear", "meniscal repair", "partial meniscectomy", "cartilage lesion"),
        "Knee", "Lower limb", "Restore swelling, range, strength, and function; repair and cartilage procedures require surgeon-specific weight-bearing and range restrictions.",
        ("IKDC or KOOS", "Effusion", "Knee range", "Quadriceps strength", "Hop/functional tests"),
        ("Repair/cartilage procedure restrictions supersede generic guidance", "Locked knee or recurrent mechanical block needs surgical review"),
        _tissue_phases(("Effusion control, extension, quadriceps activation and gait", "Range and loading only within procedure restrictions"),
                       ("Progressive quadriceps/hip strength", "Balance and single-leg control", "Graded running after objective criteria"),
                       ("Hopping, cutting and work/sport tasks", "Objective strength and function testing")),
        (MENISCUS_SOURCE,),
    ),
    _protocol(
        "adhesive_capsulitis", "Adhesive capsulitis", ("frozen shoulder",),
        "Shoulder", "Upper limb", "Irritability-matched education, mobility, and progressive function; high-irritability presentations should not be aggressively stretched.",
        ("SPADI", "QuickDASH", "Active/passive shoulder range", "Sleep and reach tolerance"),
        ("Screen diabetes/thyroid association and alternate causes", "Match mobilization and stretching intensity to irritability"),
        _tissue_phases(("Education, pain-modulated motion and sleep positioning", "Gentle self-assisted range"),
                       ("Progressive mobility and joint mobilization when indicated", "Cuff/scapular strengthening as range permits"),
                       ("End-range strength, overhead reach and work tasks", "Independent mobility/strength plan")),
        (ORTHO_SOURCE,),
    ),
    _protocol(
        "carpal_tunnel_syndrome", "Carpal tunnel syndrome", ("CTS", "median nerve compression"),
        "Wrist and hand", "Upper limb", "Education, activity/ergonomic modification, neutral wrist positioning, and selected nerve/tendon mobility with strength restoration.",
        ("Boston Carpal Tunnel Questionnaire", "QuickDASH", "Grip/pinch strength", "Sensation and thenar motor screen"),
        ("Progressive thenar weakness, constant numbness, or severe electrodiagnostic findings need medical/surgical review", "Avoid aggressive neural tensioning"),
        _tissue_phases(("Night neutral-wrist positioning and ergonomic modification", "Gentle tendon/median-nerve mobility if tolerated"),
                       ("Forearm/hand conditioning and proximal posture capacity", "Graded occupational exposure"),
                       ("Dexterity, sustained grip and work simulation", "Recurrence-prevention ergonomics")),
        (ORTHO_SOURCE,),
    ),
    _protocol(
        "nonspecific_low_back_pain", "Nonspecific low back pain", ("mechanical low back pain", "chronic low back pain", "acute low back pain"),
        "Spine", "Trunk", "Education, activity continuation, exercise matched to presentation and preference, and graded functional restoration.",
        ("Oswestry Disability Index", "Roland-Morris Questionnaire", "Patient-Specific Functional Scale", "STarT Back where appropriate"),
        ("Avoid routine pathoanatomical claims without supporting findings", "Psychosocial and occupational barriers should be assessed"),
        _tissue_phases(("Reassurance, remain active, comfortable movement and walking",),
                       ("Individualized trunk, aerobic, strength or movement-control exercise", "Graded exposure to feared or limited tasks"),
                       ("Lifting, carrying, endurance and work/recreation conditioning", "Relapse/self-management plan")),
        (LOW_BACK_SOURCE,),
    ),
    _protocol(
        "concussion_mild_tbi", "Concussion / mild traumatic brain injury", ("mTBI", "post-concussion syndrome"),
        "Neurological", "Whole body", "Multidomain rehabilitation after medical diagnosis using symptom-limited aerobic, vestibular, oculomotor, cervical, and return-to-activity progression.",
        ("Post-Concussion Symptom Scale", "Dizziness Handicap Inventory", "Vestibular/Ocular Motor Screening", "Buffalo treadmill/bike test when qualified"),
        ("Initial relative rest is brief; prolonged complete rest is generally avoided", "Return-to-play requires a stepwise medically supervised process"),
        _tissue_phases(("Medical screening, education and brief relative rest", "Light symptom-limited daily activity"),
                       ("Sub-symptom aerobic exercise", "Targeted vestibular/oculomotor and cervical treatment", "Graded cognitive and school/work exposure"),
                       ("Non-contact then contact practice under medical protocol", "Sport/work-specific exertion and clearance testing")),
        (ORTHO_SOURCE,),
        red_flags=("Worsening severe headache, repeated vomiting, seizure, deteriorating consciousness, focal deficit, or neck instability requires emergency care",),
    ),
    _protocol(
        "stroke_rehabilitation", "Stroke rehabilitation", ("CVA", "post-stroke", "hemiparesis"),
        "Neurological", "Whole body", "Interdisciplinary, task-specific, repetitive rehabilitation addressing mobility, upper limb, balance, aerobic capacity, participation, and caregiver needs.",
        ("Fugl-Meyer Assessment", "Berg Balance Scale", "10-Metre Walk Test", "6-Minute Walk Test", "Timed Up and Go", "Barthel Index"),
        ("Monitor blood pressure, exertion, cognition, neglect, falls, shoulder handling, and swallowing precautions", "Dose and supervision reflect medical stability and assistance needs"),
        _tissue_phases(("Medical stability, positioning, safe mobility and complication prevention", "Early task practice with appropriate assistance"),
                       ("High-repetition task-specific gait, transfer, balance and upper-limb practice", "Progressive aerobic and strengthening exercise", "Equipment and caregiver training"),
                       ("Community mobility, dual-task, endurance and participation goals", "Home/community exercise and secondary prevention"),
        ), (STROKE_SOURCE,),
        red_flags=("Any new FAST stroke signs require emergency activation",),
    ),
    _protocol(
        "parkinson_disease", "Parkinson disease", ("Parkinson's disease", "PD", "parkinsonism"),
        "Neurological", "Whole body", "Ongoing exercise and skilled therapy targeting amplitude, balance, gait, strength, aerobic capacity, transfers, and fall prevention.",
        ("MDS-UPDRS functional items", "Mini-BESTest", "10-Metre Walk Test", "6-Minute Walk Test", "Five Times Sit-to-Stand", "Freezing of Gait Questionnaire"),
        ("Schedule around medication response when possible", "Assess orthostatic hypotension, freezing, cognition, falls, and assistive-device safety"),
        _tissue_phases(("Baseline mobility/fall assessment and individualized exercise education", "Cueing and safe transfer/gait strategies"),
                       ("Moderate-to-vigorous aerobic exercise as medically appropriate", "Progressive resistance, balance, agility, and large-amplitude practice", "Gait/cueing and dual-task training"),
                       ("Community mobility, complex balance and participation practice", "Long-term supervised/group/home exercise plan with reassessment")),
        (PARKINSON_SOURCE,),
    ),
    _protocol(
        "total_knee_arthroplasty", "Total knee arthroplasty rehabilitation", ("TKA", "TKR", "knee replacement"),
        "Knee", "Lower limb", "Procedure-specific postoperative rehabilitation for swelling, extension/flexion, quadriceps activation, gait, strength, and function.",
        ("KOOS-JR", "Knee range", "30-second chair stand", "Timed Up and Go", "Walking and stair tolerance"),
        ("Surgeon orders, wound status, weight-bearing, and complication screening govern progression", "Do not force range through marked pain or reactive swelling"),
        _tissue_phases(("Wound/DVT screening, swelling control, extension, flexion and quadriceps activation", "Transfers, gait aid and home safety"),
                       ("Progressive lower-limb strength, balance, gait and stairs", "Aerobic and functional endurance"),
                       ("Community mobility, floor transfers and patient-valued activities", "Long-term strength/activity plan")),
        (ORTHO_SOURCE,),
    ),
    _protocol(
        "total_hip_arthroplasty", "Total hip arthroplasty rehabilitation", ("THA", "THR", "hip replacement"),
        "Hip", "Lower limb", "Procedure-specific postoperative rehabilitation for safe mobility, gait, strength, balance, and return to valued activity.",
        ("HOOS-JR", "30-second chair stand", "Timed Up and Go", "Gait speed", "Walking and stair tolerance"),
        ("Approach-specific precautions and weight-bearing orders come from the surgeon", "Screen wound, dislocation, DVT, fracture, and neurovascular complications"),
        _tissue_phases(("Safe transfers, gait aid, precautions and home program", "Gentle activation and mobility within orders"),
                       ("Progressive hip/lower-limb resistance", "Balance, gait normalization and stairs", "Aerobic conditioning"),
                       ("Community mobility, carrying and valued recreation", "Long-term strength and fall-prevention plan")),
        (HIP_OA_SOURCE, ORTHO_SOURCE),
    ),
    _protocol(
        "peripheral_vestibular_hypofunction", "Peripheral vestibular hypofunction", ("unilateral vestibular hypofunction", "bilateral vestibular hypofunction", "UVH", "BVH", "vestibular neuritis"),
        "Vestibular", "Neurological", "Diagnosis-specific vestibular rehabilitation using gaze-stability, habituation when indicated, balance, gait, and functional exposure.",
        ("Dizziness Handicap Inventory", "Activities-specific Balance Confidence Scale", "Dynamic Gait Index or Functional Gait Assessment", "Dynamic Visual Acuity", "Gait speed"),
        ("Confirm peripheral hypofunction; this pathway does not cover BPPV, central vestibular disease, or undiagnosed dizziness", "Long-term vestibular suppressants may limit compensation and warrant prescriber review"),
        _tissue_phases(
            ("Education, fall-risk assessment and safe mobility", "Gaze-stability exercise with an appropriate target and symptom dose", "Static balance with safe support"),
            ("Progress gaze-stability speed, duration and visual complexity", "Habituation only for motion-provoked symptoms", "Dynamic balance, gait with head movement and sensory reweighting"),
            ("Community mobility, uneven surfaces, dual task and patient-specific visual environments", "Independent home program and discharge criteria review"),
            return_goal="Restore stable gaze, balance, mobility, and participation with acceptable symptoms",
        ), (VESTIBULAR_SOURCE,),
        red_flags=("New focal neurological signs, severe new headache/neck pain, inability to stand, vertical or direction-changing nystagmus, or acute hearing loss requires urgent medical assessment",),
    ),
    _protocol(
        "older_adult_fall_risk", "Fall risk in community-dwelling older adults", ("falls", "recurrent falls", "balance impairment", "frailty", "fear of falling"),
        "Geriatric", "Whole body", "Multifactorial fall-risk management centered on progressive balance and strength exercise, gait, home/community hazards, and relevant medical contributors.",
        ("Timed Up and Go", "30-second chair stand or Five Times Sit-to-Stand", "4-Stage Balance Test", "gait speed", "Falls Efficacy Scale or ABC Scale", "fall history"),
        ("Review orthostatic symptoms, vision, feet/footwear, cognition, continence, medications, osteoporosis, and home hazards with the appropriate team", "Use sufficient guarding and an appropriate assistive device during challenging balance tasks"),
        _tissue_phases(
            ("Multifactorial fall-risk and home-safety assessment", "Assistive-device and transfer safety", "Begin appropriately guarded balance and functional strength"),
            ("Progressive balance challenge in standing and walking", "Lower-limb power and strength", "Gait, turning, obstacle and dual-task practice", "Physical activity and caregiver education"),
            ("Community terrain, reactive stepping and patient-specific participation", "Long-term, sufficiently challenging balance/strength program and fall-event review"),
            return_goal="Reduce modifiable fall risk and preserve safe community participation",
        ), (FALLS_SOURCE,),
        red_flags=("Fall with suspected fracture, head injury, syncope, acute neurological change, or inability to bear weight requires urgent assessment",),
    ),
    _protocol(
        "osteoporosis", "Osteoporosis / low bone mass", ("osteopenia", "low bone density", "fragility fracture risk"),
        "Bone health", "Whole body", "Progressive resistance, weight-bearing impact when appropriate, posture, balance, and safe movement education based on fracture risk and comorbidity.",
        ("30-second chair stand", "gait speed", "Timed Up and Go", "balance test", "height/posture", "patient-specific strength measures"),
        ("Known vertebral fracture or high fracture risk requires individualized loading and spinal-movement precautions", "Avoid loaded end-range spinal flexion/twisting and unsafe impact when fracture risk is high"),
        _tissue_phases(
            ("Fracture-risk, falls, posture and movement assessment", "Safe movement, lifting and floor-recovery education", "Low-risk balance and resistance entry point"),
            ("Progressive resistance for major muscle groups", "Weight-bearing impact only when appropriate", "Spinal extensor/endurance and balance training"),
            ("Functional lifting, carrying, stairs and community activity", "Sustainable resistance, weight-bearing and fall-prevention program"),
            return_goal="Improve strength, function and fall resilience while minimizing fracture risk",
        ), (OSTEOPOROSIS_SOURCE,),
        red_flags=("New severe spinal pain, height loss, or pain after minor trauma may indicate fragility fracture and requires medical assessment",),
    ),
)


PROTOCOLS_BY_ID = {protocol.id: protocol for protocol in CATALOG}
PROTOCOLS_BY_RL_INJURY = {
    protocol.rl_injury_type: protocol
    for protocol in CATALOG
    if protocol.rl_injury_type is not None
}


def list_protocols() -> list[dict[str, Any]]:
    """Return lightweight searchable catalog entries."""
    return [protocol.to_dict(detail=False) for protocol in CATALOG]


def get_protocol(condition_id: str) -> ConditionProtocol | None:
    return PROTOCOLS_BY_ID.get(condition_id)
