# DL Data Readiness Gate

GPU access never changes the following data and evaluation gates.

## Exploration only

- At least 2 reviewed exercise classes.
- At least 10 usable samples per class.
- Known modality and compatible feature/sequence contract.
- No unknown or low-confidence labels in the training subset.
- Results remain experimental and cannot be promoted.

## Candidate research model

- At least 3 reviewed classes.
- At least 30 usable samples per class.
- Participant IDs are strongly preferred and missing identity must be reported.
- Leakage-safe splits, per-class metrics, confusion analysis, and model card draft.
- Representative views and recording-quality strata.

## App-optional consideration

- Participant-grouped holdout evaluation.
- Completed model card and immutable artifact provenance.
- Acceptable macro F1 and minimum per-class recall for the declared scope.
- Confidence calibration and no unsafe systematic confusion pattern.
- Explicit safety, product, and physiotherapy review.
- Rule-based analyzers remain primary and the model is never promoted automatically.

No readiness level represents clinical validation or permits diagnostic claims.

