# Movena Full Product Roadmap

> Historical evidence: provider names and deployment status below describe earlier work.
> For the current AWS-only deployment, use [the deployment guide](aws_api_routing.md).

## Sprint 29E — First-Wave External Beta Execution

Status: **execution assets applied / beta not started**. Target is 3–5 trusted non-clinical adults after GO, but no real invitation, consent, assignment, feedback, issue, or result exists. Sprint 30 remains blocked until genuine first-wave evidence is collected safely.

## Sprint 31 — Second External Beta Wave Preparation

Status: **preparation assets complete / second wave blocked**. Sprint 30 has no real external beta evidence and unresolved P0/P1 gates remain. A header-only second-wave assignment schema and wave-aware monitoring exist, but no tester, consent, assignment, feedback, issue, invitation, or expansion is authorized. Continue Sprint 29B, then rerun Sprint 30 before reconsidering Sprint 31.

## Sprint 30 — External Beta Results Review + Fix Plan

Status: **blocked; do not start**. All five required beta CSV inputs are header-only, so there is no genuine external tester, consent, assignment, feedback, issue, reliability, safety, or privacy evidence to review. Continue Sprint 29B controlled execution. Do not expand the beta, fabricate outcomes, or advance the roadmap until genuine consented sessions exist.

## Sprint 29B — Invite First External Testers

Status: **NO-GO / not started**. Basic Render HTTPS, Supabase database readiness, auth rejection, CORS denial for an unapproved origin, and the five-exercise registry pass. The post-fix Android build is not installed, physical-device QA is absent, private feedback/support/privacy/consent/limitations links are inactive, and accountable safety/privacy approval is missing.

No real tester aliases, invitations, consent records, assignments, feedback, issues, or beta results exist. No public launch, patient use, clinical claim, new exercise, or ML/DL promotion is authorized. Sprint 30 remains blocked until controlled beta execution produces genuine feedback/issues after a future GO.

## Sprint 29 — Invite-Only External Beta Execution Assets

Status: execution assets prepared; actual external beta has not started and remains blocked. Header-only roster/consent/assignment templates, execution protocols, empty-safe monitoring, pause/cleanup controls, and report templates are available. Zero records are absence of execution evidence, not successful testing or validation.

No public release, real patient data, clinical use, diagnosis/treatment claim, new exercise, on-device analysis, or ML/DL promotion occurred. Private staging, Android build/install, physical-device QA, active feedback/support/privacy links, and a new GO approval remain required.

## Sprint 28 — External Beta Launch Candidate Fixes

Status: `0.28.0-rc.1` engineering candidate prepared; operational release remains **NO-GO**. Mobile remote configuration now fails closed without a real HTTPS API, known limitations are linked in-app, upload logging omits the source filename, and release/build/QA/retention evidence is assembled. The external issue/feedback inputs remain empty and are not treated as validation.

Private staging deployment, EAS APK submission/install, physical-device/network/token/artifact QA, active feedback/support/deletion links, and accountable approvals remain mandatory before any invitation. No public distribution, patient use, clinical claim, new exercise, on-device analysis, or ML/DL promotion occurred.

## Sprint 27 — External Closed Beta Readiness

Status: engineering/governance package prepared; operational release remains **NO-GO**. Scope, tester onboarding, consent/privacy draft, limitations, risk/support/data policies, feedback/issue schemas, analytics plan, tester pack, checklist, and summary automation are present. No invitation, public listing, patient onboarding, or clinical evaluation is authorized.

Progression to an invite-only run requires private HTTPS staging, a private Android build, physical-device/network/auth/artifact QA, active support and deletion contacts, final automated validation, and a signed multi-owner go/no-go decision. The five supported exercises, rule-based primacy, experimental ML/DL/recognition boundary, and backend-only analysis are unchanged.

## Sprint 26 — Pilot Findings Fixes and Stability Release

Status: engineering stability candidate complete; operational gate blocked. With zero submitted pilot sessions, the sprint records no participant findings. Preventive fixes cover duplicate upload submission, exercise-specific retry/camera guidance, artifact-expiry copy, pilot device metrics, and disclaimer consistency. Automated regression expanded, but private staging, APK installation, physical-device QA, and privacy/security approval remain required.

Version `0.26.0` remains internal-only. The current five analyzers and rule-based primacy are unchanged; no ML/DL promotion, on-device analysis, patient-data use, clinical claim, or public release occurred.

## Sprint 25 — Limited Internal Pilot and Feedback Loop

Status: engineering preparation complete; execution no-go. The controlled pilot scope, onboarding, safety acknowledgment, test script, QA CSV schemas, issue workflow, privacy review, build registry, readiness gate, findings template, and summary automation exist. Private staging, Android artifact installation, physical-device evidence, and named approvals are still required before any tester session.

The pilot is internal-only, uses non-identifying controlled media, and covers only `bodyweight_squat`, `sit_to_stand`, `knee_extension`, `shoulder_abduction`, and `hip_abduction`. Findings are product QA evidence, not clinical validation. No model, unsupported exercise, public distribution, or patient-data use is promoted by this sprint.

## Sprint 24 — Private Staging Deployment and Internal Pilot Gate

Status: execution package complete, external dependencies blocked. Render/Neon/Vercel is selected, staging Compose and exact runbooks exist, EAS project authentication is confirmed, and pilot documentation is ready. No real provider/database configuration, Android artifact, physical-device QA, or deployed smoke result exists; internal pilot and public release remain no-go.

## Sprint 23 — Controlled Cloud Staging Deployment

Status: repository-level staging readiness implemented. Fail-closed staging configuration, PostgreSQL/Psycopg support, internal EAS staging profile, explicit client origins, signed temporary artifacts, and release checklists are present. Actual provider deployment, signed Android build, physical-device QA, and controlled pilot approval remain gated. No public release or model promotion occurred.

Movena currently supports `bodyweight_squat`, `sit_to_stand`, `knee_extension`, `shoulder_abduction`, and the Sprint 19 `hip_abduction` rule-based MVP. All other exercises below are planned and are not production-ready. Rule-based biomechanics remains primary; ML/DL remains experimental until documented validation and promotion criteria are satisfied.

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

## Sprint 20 — Multi-Exercise UI/UX and Mobile Preparation

Status: engineering implementation complete. The product exposes a truthful exercise library and metadata API, exercise-specific recording guidance, unified result safety behavior, refined session/dashboard grouping, and a backend-analysis-first React Native/Expo plan. No new analyzer or model was added or promoted.

## Sprint 21+ — Multi-Exercise Expansion

Sprint 21 Mobile App MVP status: engineering implementation complete. The Expo Router/TypeScript client uses backend-side analysis for the five existing exercises, SecureStore for JWTs, and explicit invalid-input handling. Device testing and production privacy/security work remain release gates.

Sprint 22 Mobile QA + Cloud Deployment Preparation status: engineering hardening and documentation complete. Internal EAS profiles, upload retry/cancel, standardized errors, token-expiry cleanup, and release checklists are implemented. Status remains conditional until at least one physical Android development-build test and signed EAS build are evidenced. No public release is authorized.

Planned analyzers include balance, walking/gait screening, heel raise, lunge, and step-up. Future research may evaluate exercise recognition and validated sequence-model candidates.

Every exercise requires its own recording protocol, validity gate, phase/state logic, scoring, confidence, feedback, dataset evidence, expert review, and regression tests. Planned exercises must never be presented as working until those gates pass.

## Product-wide boundaries

- The product supports exercise monitoring and educational review; it does not diagnose or prescribe treatment.
- A licensed physiotherapist retains clinical judgment.
- Rule-based analyzers remain primary until model promotion criteria are met.
- Video, skeleton, sensor, image, and tabular datasets remain modality-separated unless a validated fusion study explicitly justifies combination.
- Mobile and cloud scale a governed product; they do not substitute for data, safety, privacy, or clinical validation.
