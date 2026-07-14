# Full Product Roadmap

## Phase 0 - Squat MVP (Current)

Maintain the working squat upload, validity gate, rule analysis, confidence, overlay, PDF report, optional experimental ML, and responsive web dashboard. Freeze its API contract while architectural seams are introduced.

## Phase 1 - Product Foundation

- Define the exercise-engine interface and registry without migrating behavior prematurely.
- Complete manual annotations, participant grouping, dataset provenance, and model governance.
- Introduce session contracts and persistence only after privacy and retention requirements are approved.
- Add observability for processing failures, latency, artifact cleanup, and confidence distributions without storing sensitive media in logs.

**Exit gate:** existing squat regression suite passes; no API behavior drift; data-governance review complete.

## Phase 2 - Second Exercise Pilot

Implement sit-to-stand as a separate rule-based analyzer using the shared pose and confidence services. Collect dedicated videos and validate rep boundaries, chair visibility, camera placement, and invalid-input behavior. Do not reuse squat thresholds.

**Exit gate:** exercise-specific tests, expert threshold review, bounded pilot evidence, and explicit limitations.

## Phase 3 - Session Experience

Add consent-aware session creation, history, report indexing, media retention choices, and export/delete controls. Keep uploads temporary by default until durable storage is explicitly enabled.

## Phase 4 - Therapist Dashboard Pilot

Add patient invitations, assigned exercise plans, review queues, longitudinal charts, therapist notes, and audit trails. This phase requires authentication, authorization, tenancy boundaries, and privacy review.

## Phase 5 - Mobile Companion

Ship a React Native + Expo client that captures or selects video, uploads to the existing backend, displays analysis and safety notices, and provides session history. Backend-side analysis remains the initial architecture.

## Phase 6 - Broader Exercise Library

Add knee extension, shoulder abduction, hip abduction, balance, then gait screening one at a time. Each exercise requires its own clinical rationale, recording protocol, validity logic, dataset, rules, feedback, and release gate.

## Phase 7 - Reliability and Research

Run participant-grouped, multi-device, multi-view, and subgroup evaluations. Experimental ML may be promoted only through the versioning and promotion policies. Clinical-study claims require a separate research, ethics, and regulatory program.

## Phase 8 - Production Operations

Harden identity, encrypted storage, regional deployment, backups, incident response, support, accessibility, performance, cost controls, and regulatory classification review. Production readiness is distinct from clinical validation.

