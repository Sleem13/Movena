# Multi-Exercise Application Expansion Plan

`bodyweight_squat`, `sit_to_stand`, and the rule-based `knee_extension` MVP are currently supported. Every other entry below is **planned**, not production-ready. Knee-extension thresholds remain engineering defaults pending representative physiotherapy review.

| Priority / exercise | Modality and landmarks | Suggested view | Rule, validity, and phase needs | Data sources / difficulty / safety |
|---|---|---|---|---|
| Implemented MVP: `knee_extension` | Video/skeleton; hip, knee, ankle | Side | Range/visibility gate; flexion → extension → return; seated-position validation | Rule-based only. Data candidates require manual review. Do not infer pain or safe load. |
| 2. `shoulder_abduction` | Video/skeleton; shoulders, elbows, wrists, hips | Front | Bilateral visibility and trunk-compensation gate; raise → peak → lower | KIMORE/UI-PRMD if protocols match. Medium. Do not infer impingement or safe range. Planned. |
| 3. `hip_abduction` | Video/skeleton; shoulders, hips, knees, ankles | Front | Support/body visibility; outward → peak → return; balance/trunk confidence | KIMORE/UI-PRMD/rehab sources after mapping. Medium-high; supervision protocol needed. Planned. |
| 4. `single_leg_balance` / `balance` | Video/skeleton; optional separate sensor track; shoulders through ankles | Front/oblique | Duration rather than reps; stance and foot visibility; loss-of-balance event definitions | Rehab24-6/KIMORE; sensor datasets stay separate. High. Never diagnose fall risk. Planned. |
| 5. `walking_gait_screen` | Video/skeleton sequence; full lower body and shoulders | Protocol-specific side/front | Walking-bout validity; gait/stride phases; camera-motion rejection | Gait sources; sensors remain separate. Very high. Screening only; no pathology claims. Planned. |
| 6. `heel_raise` | Video/skeleton; knees, ankles, heels/feet where supported | Side/rear | Foot visibility; rise → peak → lower; small-motion robustness | Curated high-resolution video likely required. High due to foot landmark limits. Planned. |
| 7. `lunge` | Video/skeleton; shoulders, hips, knees, ankles | Side for depth, front for alignment | Stance/orientation; descent → bottom → ascent; leading-leg detection | UI-PRMD/exercise sources after exact protocol match. High; variants need separate rules. Planned. |
| 8. `step_up` | Video/skeleton; shoulders, hips, knees, ankles | Side | Step visibility/height; approach → ascent → stand → descent; leg identification | Curated/compatible rehab video. High; occlusion and fall precautions matter. Planned. |

## Activation gate

Each exercise needs its own camera protocol, schema, validity gate, rep/phase logic, rule-based scoring, confidence behavior, safety feedback, representative real-video tests, dataset evidence, and expert review. ML/DL is optional and remains subordinate to the rule-based path.

## Feature delivery sequence

1. Identify and audit dataset support.
2. Update the exercise taxonomy without activating the exercise.
3. Design an exercise-specific rule-based analyzer.
4. Implement its validity gate.
5. Implement rep/phase logic.
6. Add transparent scoring and confidence.
7. Add the frontend option only after backend activation.
8. Adapt overlay and report output.
9. Train ML/DL only when labels, participants, and modality support it.
10. Keep the model experimental until promotion criteria pass.

Sprint 16A recognition may suggest a taxonomy label, but it does not activate an expansion step or analyzer. Unsupported predictions remain planned-only, and the user must confirm an available exercise manually.

Sprint 15 coverage and readiness reports inform steps 1–2 only. Sprint 17 separately implemented the exercise-specific knee-extension gates; this does not clinically validate its thresholds or make candidate data training-ready.
