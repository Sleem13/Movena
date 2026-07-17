# Backend Exercise Engine Architecture

## Analyzer catalog

Current supported analyzers:

- `bodyweight_squat`
- `sit_to_stand`
- `knee_extension`

Planned analyzers—not implemented or production-ready—include `shoulder_abduction`, `hip_abduction`, `balance`, and `walking_gait_screen`. Heel raise, lunge, and step-up are later planned candidates. Knee extension has exercise-specific validity, phase, scoring, and feedback rules.

## Exercise contract

Each analyzer should expose stable metadata and return a shared result envelope containing exercise/version, validity, status, repetitions or duration, exercise-specific metrics, score or null, detected observations, educational feedback, confidence, limitations, and optional frame details. A registry resolves only explicitly activated exercise IDs and rejects unknown or planned-only entries.

## Required pipeline for every future analyzer

1. **Validity gate:** exercise-specific pose coverage, view, body visibility, motion, and complete-attempt criteria.
2. **State machine / phase detection:** explicit phases with hysteresis, timing, partial-attempt handling, and rep/event confidence.
3. **Movement scoring:** transparent, versioned rule components supported by the recording view; invalid attempts receive no normal score.
4. **Confidence scoring:** pose quality, signal stability, protocol/view fit, event confidence, and warnings.
5. **Safety feedback:** observational and educational wording, stop guidance, limitations, and professional-review advice.
6. **Optional ML/DL:** only after exercise- and modality-specific validation; never overrides validity or the primary rule-based analyzer.

## Shared versus exercise-specific responsibilities

Shared services cover upload validation, temporary media, pose backends, geometry primitives, artifact/report handling, logging, errors, and confidence mechanisms. Each exercise owns its required landmarks/views, validity thresholds, phases, scoring, observations, feedback, dataset evidence, and version provenance. Squat thresholds must not be reused for sit-to-stand or future exercises merely because landmarks overlap.

## Activation and testing gate

Activation requires representative valid/invalid real-video fixtures, geometry and state-machine tests, API contract tests, expert threshold review, confidence/safety checks, bounded performance evaluation, and explicit limitations. A dataset adapter or taxonomy entry alone does not activate an analyzer.
