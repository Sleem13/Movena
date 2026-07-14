# Optional Model Promotion Criteria

Promotion means eligibility as an optional, clearly labeled second opinion. It does not mean clinical validation, diagnosis, treatment guidance, or replacement of the rule-based analyzer.

## Blocking Data Gates

- At least 30 independently reviewed real videos per supported class.
- At least 10 participants per class, with varied sessions and acquisition conditions.
- 100% completion of expected reps, participant ID, session ID, view, recording quality, annotator, and annotation confidence for evaluation rows.
- No unresolved duplicate paths, label conflicts, or participant leakage.
- A frozen participant-grouped train/validation/holdout split with every class represented in validation and holdout.
- Augmented samples remain traceable to real sources and are excluded as independent holdout evidence.

## Blocking Engineering Gates

- Reproducible dataset, feature, dependency, and model versions.
- Macro F1 of at least 0.80 on the frozen real participant-grouped holdout.
- Recall of at least 0.70 for every supported class on that holdout.
- Error review finds no systematic failure hidden by aggregate metrics.
- Confidence behavior, missing-pose behavior, and invalid-input behavior pass regression tests.
- Independent reviewer approval of labels, limitations, and user-facing wording.

These numeric thresholds are internal engineering promotion gates, not clinical-performance standards. Meeting them does not establish clinical effectiveness.

## Product and Safety Gates

- The rule-based analyzer remains primary.
- ML remains optional, visibly experimental, and unable to override validity rejection or rule-based safety feedback.
- No diagnostic, treatment, recovery, injury-risk, or clinical-accuracy claim is introduced.
- Rollback to the prior trusted artifact is documented and tested.

## Current Decision

V2 fails the data gates: manual annotations are incomplete, participant grouping is unavailable, class coverage is insufficient, and the holdout is too small. **Do not promote v2.**

