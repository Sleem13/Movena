# Experimental ML Integration Design

The rule-based analyzer remains primary. `POST /api/v1/analyze/squat` returns no ML result by default. With `include_ml=true`, the backend aggregates detected pose frames into the same 45 unique ordered features saved in `models/squat_baseline/feature_columns.json`, validates both feature and label contracts against the trusted joblib bundle, and returns an optional second opinion.

The service loads artifacts lazily so startup and ordinary rule analysis do not depend on ML availability. Missing packages, artifacts, contract mismatches, aggregation errors, or inference errors return `enabled: false` and “Rule-based analysis is still available.” They do not change repetitions, score, issue flags, feedback, or HTTP success.

Joblib deserialization can execute code. The service loads only the project-controlled artifact path and never an uploaded model. The baseline is experimental, not clinically validated, and must not be shown as diagnosis or authoritative form classification.
