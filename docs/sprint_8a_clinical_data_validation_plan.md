# Sprint 8A Clinical and Data Validation Plan

## Purpose

Sprint 8A hardens dataset provenance, human annotation, participant independence, and error review for the existing squat-only MVP. It does not add exercises, deep learning, diagnostic claims, or replacement of the rule-based analyzer.

## Current Baseline

- 23 labeled real videos are present in the v2 feature dataset.
- One unlabeled video remains quarantined.
- No augmented feature rows are currently available.
- Manual expected-rep, participant, session, view, and recording-quality metadata are incomplete.
- The existing three-video holdout is not known to be participant independent.
- `squat_fast_uncontrolled` is absent; shallow-depth has only two real videos.

## Workflow

1. Generate `manual_rep_annotations.csv` from current real and safe augmented registries.
2. Complete annotations through frame-reviewed human assessment; never infer identity or repetitions automatically.
3. Validate completeness, identifier syntax, duplicates, class coverage, and participant distribution.
4. Generate a participant-grouped split. Incomplete rows remain explicitly unassigned.
5. Freeze the grouped split before retraining or threshold comparison.
6. Retrain a new versioned candidate only after the split is ready.
7. Run holdout error analysis by class, view, and recording quality.
8. Apply the documented promotion gates. Failure of any blocking gate keeps v2 experimental.

## Current Sprint 8A Decision

The workflow is operational, but the data is not promotion-ready. Manual annotations and participant metadata must be completed, missing classes collected, and the grouped split frozen before a participant-independent model evaluation is possible.

