# Participant-Grouped Evaluation

## Why Grouping Is Required

Clips from the same person or session can share appearance, movement pattern, camera, clothing, and environment. Placing that participant in both development and holdout sets creates identity and acquisition leakage and can exaggerate apparent reliability.

## Split Rules

- Every participant belongs to exactly one of `train`, `validation`, or `holdout`.
- All sessions and augmented variants for that participant inherit the same group.
- Unlabeled or unsupported rows are excluded.
- Missing or invalid participant IDs remain `unassigned`.
- The deterministic allocator targets 70% train, 15% validation, and 15% holdout while approximating class balance at participant-group level.
- The generated split must be frozen before retraining and must not be tuned in response to holdout errors.

## Minimum Readiness

All three partitions must contain participant groups, no participant may cross partitions, and every supported class should be represented in validation and holdout. Class and participant counts must be reported separately; augmented rows do not increase participant counts.

The current dataset has no completed participant identifiers. Therefore, the generated Sprint 8A split is an explicit unassigned inventory, not a valid evaluation split.

