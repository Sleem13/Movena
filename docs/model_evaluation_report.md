# Model Evaluation Report

## Scientific Status

This is an experimental engineering baseline, not a clinically validated model. The protected holdout contains only three videos and does not contain every class. Metrics are descriptive smoke-test evidence only.

## Saved Baseline

- Model: `svc_rbf`
- Holdout rows: 3
- Accuracy: 0.6667
- Macro precision: 0.5000
- Macro recall: 0.6667
- Macro F1: 0.5556
- Weighted F1: 0.5556
- Confusion matrix: `[[1, 0, 0, 0], [0, 0, 0, 0], [1, 0, 0, 0], [0, 0, 0, 1]]`
- Figure: `reports\figures\squat_baseline_confusion_matrix.png`

The holdout must not be used to tune thresholds or repeatedly select production behavior. More independently labeled videos per class are required before meaningful validation.
