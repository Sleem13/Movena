# ML Model Versioning Policy

- `sprint_5_baseline` is the current optional backend baseline.
- `sprint_7_baseline_v2` is an offline candidate only.
- The backend must not switch artifacts merely because v2 trained successfully or matched a tiny holdout score.
- Promotion requires stronger real-data coverage, participant-grouped validation, a frozen representative holdout, schema compatibility, regression tests, artifact provenance, dependency compatibility, and documented approval.
- Every bundle stores model name, model version, feature order, label mapping, and experimental warning.
- Historical comparisons use immutable reference metrics. Sprint 7 uses `models/squat_baseline/sprint_5_reference_metrics.json`; a regenerated generic `metrics.json` must never silently redefine the Sprint 5 baseline.
- A versioned artifact must not be overwritten with a different dataset while retaining the same model version. Retraining requires a new version directory or an explicitly marked development artifact.
- Joblib artifacts are trusted code-bearing files and must never be loaded from user uploads.
- Rollback must retain the prior trusted artifact and contract.
- The rule-based analyzer remains primary across every model version.

Current promotion decision: **do not promote v2; keep ML optional and disabled by default.**
