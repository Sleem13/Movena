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
3. Validate completeness, categorical values, identifier syntax, duplicates, class coverage, and participant/source distributions; retain row-level validation results.
4. Generate the privacy-conscious participant metadata template and complete reviewed demographic-group fields without direct identifiers.
5. Generate a participant-grouped split. Incomplete rows remain explicitly unassigned, and the report audits class and dataset-source balance.
6. Evaluate the current rep counter only against completed human rep counts; skip unavailable evidence without changing analyzer thresholds.
7. Freeze the grouped split before retraining or threshold comparison.
8. Retrain a new versioned candidate only after the split is ready.
9. Run holdout error analysis by class, dataset source, participant, view, recording quality, split, and confidence where evidence exists.
10. Apply the documented promotion gates. Failure of any blocking gate keeps v2 experimental.

## Current Sprint 8A Decision

The workflow is operational, but the data is not promotion-ready. Manual annotations and participant metadata must be completed, missing classes collected, and the grouped split frozen before a participant-independent model evaluation is possible.
