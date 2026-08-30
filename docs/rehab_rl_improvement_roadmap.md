# RehabRL improvement roadmap

This roadmap prioritizes the work required to move RehabRL from an integrated
research feature toward governed clinical decision support. It is not a claim
that the current policy is clinically validated.

## P0 — Safety and governance before real-patient use

1. **Independent clinical review**
   - Review every injury, recovery stage, action template, contraindication,
     pain ceiling, progression rule, and fallback with licensed clinicians.
   - Record clinical owners, approval dates, intended use, and excluded use.
2. **Benchmark against clinical baselines**
   - Compare the policy with guideline-based and clinician-selected actions.
   - Report unsafe-action rate, constraint violations, regret, calibration, and
     subgroup outcomes—not simulated reward alone.
3. **Hard safety constraints and abstention**
   - Enforce contraindications outside the learned policy.
   - Abstain on out-of-distribution, incomplete, contradictory, or high-risk
     patient states and route them to manual review.
4. **Versioned clinical audit trail**
   - Persist input provenance, policy/checkpoint version, candidate output,
     clinician decision, edits, rejection reason, and timestamps.
5. **Production training lockout**
   - Disable in-process training by default in staging/production until durable
     jobs, approval gates, artifact review, and rollback exist.

## P1 — Clinical workflow integration

1. Link assessments to an authorized patient profile and active care-plan item.
2. Prefill only validated measures from PhysioVision sessions; require clinician
   confirmation before policy execution.
3. Add approve, modify, reject, and supersede states for recommendation records.
4. Show the exact rationale, constraints, model version, and data completeness
   beside every candidate.
5. Add notifications and review queues without exposing policy output directly
   to patients before clinician approval.

## P1 — Reliable model operations

1. Move training to a durable queue/worker with shared status and cancellation.
2. Store immutable artifacts in versioned object storage with hashes and signed
   metadata.
3. Add a model registry state machine: experimental → candidate → approved →
   active → retired.
4. Require automated evaluation gates and two-person approval before activation.
5. Add one-click rollback to the previous approved policy.

## P2 — Data and evaluation quality

1. Build patient-grouped train/validation/test splits with provenance and license
   tracking.
2. Evaluate across injury type, recovery stage, age band, sex, mobility level,
   device/source, and missing-data pattern where collection is lawful.
3. Add off-policy evaluation and uncertainty estimates before prospective use.
4. Calibrate confidence against held-out clinical decisions; do not present the
   current Q-value spread as clinical probability.
5. Monitor input drift, action distribution, abstention, clinician overrides,
   safety events, and outcome follow-up after approval.

## P2 — Security and privacy

1. Threat-model recommendation tampering, checkpoint replacement, training-job
   abuse, and unauthorized patient linkage.
2. Encrypt and access-control persisted assessment inputs and outputs.
3. Add rate limits and audit events for assessment, restore, and training APIs.
4. Verify deletion, retention, export, consent, and incident-response behavior.
5. Sign artifacts and validate hashes before loading a checkpoint.

## P3 — Product and accessibility

1. Complete Arabic localization for the full RehabRL workspace and clinical
   terminology review.
2. Add keyboard, screen-reader, contrast, zoom, and reduced-motion validation.
3. Provide side-by-side candidate comparison and clear change explanations.
4. Add print/export only after recommendation persistence and authorization are
   implemented.
5. Extend mobile access only after clinician approval workflows and responsive
   safety review are complete.

## Suggested first delivery slice

The next implementation should combine four tightly related controls:

1. A production feature flag that disables training and checkpoint restore.
2. A versioned recommendation/audit schema with approve/reject workflow.
3. A hard safety constraint layer with explicit abstention reasons.
4. A reproducible clinical-baseline evaluation report for the packaged policy.

This slice reduces the highest operational and clinical risks before expanding
features or collecting more data.
