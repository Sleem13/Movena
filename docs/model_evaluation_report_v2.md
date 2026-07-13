# Model Evaluation Report v2

## Status

Preliminary experimental baseline; not clinically validated. The holdout contains 3 real videos.

- Holdout classes: squat_correct, squat_shallow_depth, squat_trunk_lean
- Missing holdout classes: squat_knee_valgus
- Candidate: `svc_rbf`
- Accuracy: 1.0000
- Macro precision: 1.0000
- Macro recall: 1.0000
- Macro F1: 1.0000
- Weighted F1: 1.0000
- Confusion matrix: `[[1, 0, 0, 0], [0, 0, 0, 0], [0, 0, 1, 0], [0, 0, 0, 1]]`

These values are engineering smoke-test evidence. They must not be reported as clinical accuracy or used to enable ML by default.
