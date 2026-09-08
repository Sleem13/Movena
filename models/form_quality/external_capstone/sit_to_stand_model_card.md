# Sit-to-Stand PRMD Candidate Model Card

## Status

Deployment status: **blocked**.

This card documents the inspected candidate. It is not an approval to enable,
redistribute, or use the model for clinical decisions.

## Model

- Artifact: sit_to_stand_robust.keras
- SHA-256: 99b18cf621a3fa4d113fbe557f9998fba5e501e5bde67f635b0d8dd92d6b6f00
- Architecture: two bidirectional LSTM layers followed by dense regression
- Input: one (88, 66) sequence representing 22 UI-PRMD joints in 3D
- Preprocessing: root centering and per-frame pelvis-width normalization
- Output: one sigmoid scalar, calibrated by the source app from 0.60 to 0.96
  for an experimental 0-100 comparison

## Intended Use

After all gates pass, the candidate may provide an optional movement-pattern
comparison for a therapist reviewing an already accepted Movena sit-to-stand
analysis. Movena's rule-based validity, rep count, score, warnings, and
therapist-guided care workflow remain primary.

## Prohibited Use

- Diagnosis, treatment selection, safety clearance, prognosis, or recovery-time
  estimation.
- Overriding a rejected recording or a rule-based safety warning.
- Autonomous patient coaching.
- Public distribution before rights and training-data lineage are confirmed.

## Evidence And Limitations

The source report lists favorable held-out metrics, but also describes
model-selection leakage because a test fold was used for validation and
checkpoint selection. Movena has not independently reproduced the training
pipeline or validated this artifact on representative Movena recordings,
camera setups, demographics, assistive devices, or clinical populations.

## Required Approvals

- [ ] Written license and redistribution rights for code and weights.
- [ ] Training-dataset lineage and derivative-model rights.
- [ ] Independent participant-grouped Movena validation.
- [ ] Clinician review of the sit-to-stand protocol and output language.
- [ ] Linux deployment-image artifact load and inference smoke test.
- [ ] Performance, drift, monitoring, rollback, and incident-response review.
