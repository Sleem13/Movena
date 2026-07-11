# Squat Quality Baseline

This directory contains the reproducible Sprint 5 custom-video baseline. It is experimental and not clinically validated. It does not replace the rule-based analyzer.

- `metrics.json`: candidate and saved-model holdout evidence plus data warnings.
- `feature_columns.json`: ordered 46-feature inference contract.
- `label_mapping.json`: deterministic alphabetical label mapping.
- `artifacts/squat_quality_baseline.pkl`: joblib bundle containing the selected pipeline and metadata.

The artifact was trained on 13 development/reference-validation videos and evaluated on three protected holdout videos. Knee valgus has one development video and no holdout example. Do not interpret the reported metrics as generalization, safety, diagnostic, or clinical performance.

Rebuild from the repository root using the four Sprint 5 commands in `README.md`. Pickle/joblib files must only be loaded from trusted project artifacts because deserialization can execute code.
