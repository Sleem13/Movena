# Optional Model Promotion Criteria

Promotion means eligibility as an optional, clearly labeled engineering candidate. It does not mean clinical validation, diagnosis, treatment guidance, or replacement of the rule-based analyzer.

## Blocking Evidence Gates

- Manual annotation completion is at least 90% and all evaluation rows are complete.
- A frozen participant-grouped train/validation/holdout split has no participant leakage.
- The holdout contains at least five participants, preferably substantially more, and represents all target classes.
- Each target class has at least 10 independently reviewed real videos before serious promotion discussion; broader participant diversity is preferred.
- Augmented samples remain traceable to real sources and are never treated as independent holdout evidence.
- Macro F1 is at least 0.75 on the real participant-grouped holdout.
- Recall is at least 0.70 for every major supported class, and no class has zero recall.
- Low-confidence behavior is documented and unsafe-looking systematic error patterns receive PT-informed review.
- Dataset, feature, dependency, split, and model versions are reproducible.

## Product and Safety Gates

- The rule-based analyzer remains primary.
- ML remains optional, visibly experimental, and cannot override input validity or rule-based safety feedback.
- No diagnostic, treatment, recovery, injury-risk, or clinical-accuracy claim is introduced.
- Limitations and rollback behavior are documented and tested.

These thresholds are internal engineering/research criteria, not clinical-performance standards. Passing them would support candidate evaluation only.

## Current Decision

V2 does not meet the evidence gates: manual annotations and participant metadata are incomplete, a promotion-grade participant-grouped holdout is absent, coverage is underpowered, and the current protected holdout is too small. **Do not promote v2; it remains experimental.**
