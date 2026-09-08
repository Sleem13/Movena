# PRMD Production Readiness

## Current Decision

The Movena integration software is deployable behind fail-closed gates, but the
external sit-to-stand model is **not approved for production enablement**.
License, data lineage, independent validation, clinician review, and a real
Linux runtime smoke test remain incomplete.

## Implemented Production Controls

- Named MediaPipe-to-UI-PRMD feature mapping with visibility, finite-value,
  subject-continuity, shape, and normalization checks.
- Catalog-controlled provider loading with explicit enablement and three
  approval fields.
- Artifact paths confined to PRMD_MODEL_ROOT.
- SHA-256 verification before model load and again inside the cached loader.
- Lazy TensorFlow import so the rule-based API remains available without the
  optional runtime.
- Strict input-shape, scalar-output, finite-value, and calibration validation.
- Read-only GET /api/v1/ml/readiness status for frontend and operations.
- REQUIRED_ML_EXERCISES startup gate for deployments that require a provider.
- Frontend availability state and verified-artifact result presentation.

## Deployment Contract

Build the optional runtime only for an approved deployment:

    docker build --build-arg INSTALL_PRMD_RUNTIME=true -t movena-api:prmd .

Mount approved model artifacts into a read-only directory and configure:

    ENABLE_ML_SECOND_OPINION=true
    ML_SECOND_OPINION_CATALOG=/app/config/prmd-catalog.json
    PRMD_MODEL_ROOT=/app/model-artifacts/prmd
    REQUIRED_ML_EXERCISES=sit_to_stand

The production catalog must set enabled, license_status, validation_status, and
clinician_review_status to approved values and must contain the exact deployed
artifact SHA-256. Startup fails if a required model is disabled, blocked,
missing, modified, or unable to load its runtime.

## Verification Evidence

- Provider and adapter paths are covered with synthetic contract tests.
- Failure modes preserve rule-based analysis and return an unavailable status.
- TensorFlow 2.21 installed in a temporary Windows test environment, but local
  Application Control blocked the native ml_dtypes extension before the legacy
  Keras artifact could load.
- Docker and WSL are unavailable in the current workstation environment, so
  the required Linux artifact-load and inference smoke test remains open.

## Enablement Checklist

1. Obtain written rights for the model, source code, and dataset derivatives.
2. Run independent participant-grouped validation using the frozen artifact.
3. Complete clinician review and approve the model card.
4. Build the Linux image with INSTALL_PRMD_RUNTIME=true.
5. Mount the artifact read-only and verify its SHA-256.
6. Confirm /api/v1/ml/readiness reports sit_to_stand as ready.
7. Start with REQUIRED_ML_EXERCISES=sit_to_stand and run a golden-video smoke
   test before receiving real user data.
8. Add monitoring for provider failures, latency, output distribution, and
   disagreement without storing raw video beyond the approved retention policy.
