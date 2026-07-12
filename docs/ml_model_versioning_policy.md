# ML Model Versioning Policy

- `sprint_5_baseline` is the current optional backend baseline.
- `sprint_7_baseline_v2` is an offline candidate only.
- The backend must not switch artifacts merely because v2 trained successfully or matched a tiny holdout score.
- Promotion requires stronger real-data coverage, participant-grouped validation, a frozen representative holdout, schema compatibility, regression tests, artifact provenance, dependency compatibility, and documented approval.
- Every bundle stores model name, model version, feature order, label mapping, and experimental warning.
- Joblib artifacts are trusted code-bearing files and must never be loaded from user uploads.
- Rollback must retain the prior trusted artifact and contract.
- The rule-based analyzer remains primary across every model version.

Current promotion decision: **do not promote v2; keep ML optional and disabled by default.**
