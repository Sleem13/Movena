# Sprint 8A Model Error Analysis v2

## Scope

This analysis covers only the existing real protected holdout. It is engineering evidence, not clinical validation.

- Evaluated videos: 3
- Correct predictions: 3
- Misclassifications: 0

## False Negatives by Actual Class

- None

## False Positives by Predicted Class

- None

## Errors by View Type

- None

## Errors by Recording Quality

- None

## Errors by Dataset Source

- None

## Confusion Matrix

```
predicted            squat_correct  squat_shallow_depth  squat_trunk_lean
actual
squat_correct                    1                    0                 0
squat_shallow_depth              0                    1                 0
squat_trunk_lean                 0                    0                 1
```

## Reliability Decision

Insufficient evidence for promotion. The v2 model remains experimental because the current holdout is small, participant grouping is incomplete, manual annotations are incomplete, and class coverage is insufficient.

The rule-based analyzer remains primary. No diagnostic or treatment claim is supported.
