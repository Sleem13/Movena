# Next Exercise Selection

## Ranking Method

Exercises are ranked by physiotherapy usefulness, ease of consistent video capture, available data, rule/state-machine complexity, safety risk, and demonstration value. Scores are relative planning judgments, not evidence of clinical effectiveness.

| Rank | Exercise | Clinical usefulness | Recording ease | Data outlook | Algorithm complexity | Safety risk | Demo value |
|---:|---|---|---|---|---|---|---|
| 1 | Sit-to-stand | High | High | Moderate | Moderate | Low-moderate | High |
| 2 | Knee extension | High | High | Moderate | Low-moderate | Low | Medium-high |
| 3 | Shoulder abduction | High | High | Moderate | Moderate | Low-moderate | High |
| 4 | Hip abduction | Moderate-high | Moderate | Limited-moderate | Moderate | Moderate | Medium |
| 5 | Balance | High | Moderate | Mixed | High | Higher | High |
| 6 | Gait/walking screen | High | Low-moderate | Available but heterogeneous | Very high | Moderate-higher | High |

## Why Sit-to-Stand Is Next

Sit-to-stand is functionally meaningful, familiar to users, recordable with a fixed front or side camera, and shares reusable concepts with squat—hip/knee flexion, trunk motion, phases, repetitions, visibility, and confidence—without being the same exercise. It demonstrates that the engine can support an external object (chair), a different start/end posture, and exercise-specific rules.

The analyzer must define chair visibility, seated stability, lift-off, standing completion, controlled return, hand support, camera view, and partial attempts. Squat thresholds and scores must not be copied.

## Later Exercises

- **Knee extension:** relatively simple single-joint phases; requires side/limb identification, seated setup, range and tempo rules.
- **Shoulder abduction:** strong visual demo; requires frontal-plane view, side selection, trunk compensation, and overhead visibility.
- **Hip abduction:** useful but sensitive to camera plane, stance support, pelvic compensation, and balance.
- **Balance:** clinically useful but safety-sensitive; requires support context, duration, sway definitions, and fall-risk-safe protocol. The product must not claim fall-risk diagnosis.
- **Gait/walking screen:** requires longer capture, multiple cycles, spatial calibration or careful normalization, occlusion handling, and substantially broader validation.

## Sit-to-Stand Entry Gate

Before implementation: approve a recording/safety protocol, collect participant-grouped real examples, define expert-reviewed validity and rep labels, document hand-support handling, establish rule thresholds, and add invalid-input/low-confidence tests. No new model training is required for the first rule-based pilot.
