# PhysioVision AI Full Product Roadmap

PhysioVision AI currently supports `bodyweight_squat`, `sit_to_stand`, `knee_extension`, `shoulder_abduction`, and the Sprint 19 `hip_abduction` rule-based MVP. All other exercises below are planned and are not production-ready. Rule-based biomechanics remains primary; ML/DL remains experimental until documented validation and promotion criteria are satisfied.

## Sprint 12 — Deployment & Mobile-Ready API Hardening

Purpose: environment configuration, explicit CORS, upload validation, standardized errors, health/readiness endpoints, a mobile API contract, artifact cleanup, and deployment preparation.

Status: engineering complete. This does not authorize processing real patient data.

## Sprint 13 — Auth + Roles + Privacy Foundation

Purpose: establish user identity and patient, therapist, and administrator roles; protect sessions; separate therapist and patient access; define privacy and consent placeholders; and document production safety requirements.

Exit gate: authenticated and authorized resource access, privacy-reviewed retention/deletion behavior, audit foundations, and tests. Development/demo data must remain non-identifiable.

Status: local JWT development foundation implemented. Production identity, consent, tenancy, audit operations, and privacy approval remain gated work.

## Sprint 14 — Multi-Dataset ML/DL Expansion Architecture

Purpose: classify dataset modalities, establish an exercise taxonomy and unified sample schema, define the dataset-adapter interface, separate ML/DL training tracks, introduce a model registry, and create a model-card template.

No datasets are blindly merged and no model becomes primary during this sprint.

Status: architecture and safe dry-run scaffolds implemented; exercise-specific parsing and training readiness remain Sprint 15 work.

## Sprint 15 — Exercise-Specific Dataset Adapters

Purpose: implement governed adapters for KIMORE, UI-PRMD, UCI physical-therapy data, DynTherapy, Rehab24-6, and available physical-therapy exercise datasets. Each adapter produces a dataset-specific training-readiness report covering modality, labels, provenance, participants, splits, quality, licensing, and limitations.

Adapter availability does not mean the related exercise analyzer is supported.

## Sprint 16 — Mobile App MVP

Purpose: build a React Native + Expo client with login/demo mode, exercise selection, video recording/upload, progress, analysis results, session history, and safety/about content. Analysis remains backend-side initially.

Only supported backend exercises may appear as active choices.

### Sprint 16A â€” Exercise Recognition Model Foundation

Status: engineering foundation implemented. Recognition metadata and features remain modality-separated, baseline training is gated, and the optional API returns experimental suggestions only. Current reviewed features contain one exercise class, so no recognition model is trained or promoted. Manual selection remains primary; squat, sit-to-stand, knee extension, shoulder abduction, and hip abduction have rule-based analyzers.

## Sprint 17 — Knee Extension Analyzer MVP

Status: engineering implementation complete. The manually selected workflow has exercise-specific validity, phase logic, scoring, feedback, API/UI support, and shared artifacts. Candidate data remains manual-review-only and no ML model was trained or promoted.

## Sprint 17B — Cloud Deployment

Purpose: deploy backend, frontend, database, and secure media/object storage; configure environment variables and production CORS; and establish logging, monitoring, backup, security, and privacy procedures.

Cloud deployment follows API hardening, auth/privacy, stable session contracts, and dataset/model registry clarity. It is separate from clinical validation.

## Sprint 18 — Shoulder Abduction Analyzer MVP

Status: engineering implementation complete. The manually selected workflow has front-view geometry, exercise-specific validity and phase logic, explainable scoring, safe feedback, API/UI/session support, and manual-review-only dataset preparation. No ML/DL model was trained or promoted.

## Sprint 19 — Hip Abduction Analyzer MVP

Status: engineering implementation complete. The manually selected standing workflow has front-view geometry, moving-side selection, exercise-specific validity and phase logic, explainable scoring, safe feedback, API/UI/session support, and manual-review-only dataset preparation. No ML/DL model was trained or promoted.

## Sprint 20+ — Multi-Exercise Expansion

Planned analyzers include balance, walking/gait screening, heel raise, lunge, and step-up. Future research may evaluate exercise recognition and validated sequence-model candidates.

Every exercise requires its own recording protocol, validity gate, phase/state logic, scoring, confidence, feedback, dataset evidence, expert review, and regression tests. Planned exercises must never be presented as working until those gates pass.

## Product-wide boundaries

- The product supports exercise monitoring and educational review; it does not diagnose or prescribe treatment.
- A licensed physiotherapist retains clinical judgment.
- Rule-based analyzers remain primary until model promotion criteria are met.
- Video, skeleton, sensor, image, and tabular datasets remain modality-separated unless a validated fusion study explicitly justifies combination.
- Mobile and cloud scale a governed product; they do not substitute for data, safety, privacy, or clinical validation.
