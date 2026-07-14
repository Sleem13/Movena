# Sprint 8A Clinical/Data Validation Report

## Scope

Sprint 8A adds PT-informed data review and reliability tooling around the existing squat-only system. It does not alter squat analysis, train a new model, establish clinical validity, or make ML primary.

## Validation Run Status

- Annotation template: 24 rows generated; all 24 existing rows were preserved.
- Annotation completion: 0 of 24 rows (0.00%) currently meet the required annotation checks.
- Participant metadata: zero reviewed participant IDs are available, so the generated template currently contains its schema and no participant rows.
- Participant split: 0 of 24 videos are assigned; all remain unassigned pending reviewed participant IDs.
- Rep-count evaluation: zero videos have completed `expected_reps`, so no accuracy metric is currently estimable.
- Model error analysis: three existing real protected holdout videos were evaluated with zero observed errors, but their size and unknown participant independence are insufficient evidence for promotion.
- Automated regression: 47 configured top-level tests and 110 combined top-level/backend tests pass.

## Promotion Decision

The v2 model remains experimental. Promotion is blocked until manual annotations are substantially complete, participant/session metadata supports an independent grouped holdout, every target class has adequate real coverage, and holdout metrics meet the internal promotion gates. The rule-based analyzer remains the primary product output.

## Remaining Limitations

- Most human annotation fields are currently incomplete.
- Participant independence cannot be established for rows without reviewed pseudonymous IDs.
- Missing and underrepresented classes prevent reliable per-class conclusions.
- Aggregate metrics from a very small holdout are unstable and are not clinical evidence.

## Recommended Actions

1. Complete a first PT-reviewed annotation pass and second-review uncertain clips.
2. Populate pseudonymous participant/session metadata and regenerate the grouped split.
3. Collect consented real videos for missing and underrepresented classes and views.
4. Freeze an adequately sized real participant-grouped holdout before retraining or promotion review.
