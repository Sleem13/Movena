# Movena Development Journey

This document preserves the chronological sprint history that previously dominated the project READMEs. The main [README](../README.md) now describes the current product and setup, while this file records how the platform evolved.

## Journey summary

Movena began as a squat-analysis MVP, then expanded through five broad phases:

1. Establish a reliable video, pose, repetition, and feedback pipeline.
2. Add confidence handling, datasets, ML experiments, and additional exercises.
3. Add persistence, therapist workflows, authentication, privacy, and deployment hardening.
4. Build web and Android product experiences around the backend analyzers.
5. Add temporal exercise recognition, subject tracking, deployed staging, and a simplified mobile UX.

## Sprint timeline

| Sprint | Focus | Main outcome |
|---|---|---|
| 1 | Squat MVP | FastAPI upload endpoint, initial MediaPipe pose extraction, squat geometry, repetition logic, and basic feedback. |
| 1.5 | Engineering review | Corrected environment, dependency, test-runner, validation, and architecture problems discovered after the initial MVP. |
| 2 | Frontend and pipeline stabilization | Added the first React upload/results experience, configurable API URL, validation, and dataset preparation foundations. |
| 3 | Analysis quality | Improved squat phases, issue reporting, metrics, API contracts, and frontend result presentation. |
| 4 | Validation and reporting | Strengthened tests, structured result fields, confidence communication, and report-oriented outputs. |
| 5 | Baseline ML | Added an experimental posture-classification track alongside the primary biomechanics rules. |
| 6 | ML and annotated video | Integrated optional second-opinion inference and pose-overlay video generation without replacing rule-based analysis. |
| 6.6 | Repetition stabilization | Hardened squat cycle detection against jitter, partial motion, and unstable phase transitions. |
| 7 | Dataset expansion | Formalized dataset provenance, training splits, reliability evaluation, and larger squat-data preparation. |
| 7.5 | Multi-dataset registry | Added dataset adapters and registry conventions so multiple sources could coexist reproducibly. |
| 8A | Clinical/data validation | Added stricter validation gates, confidence interpretation, error analysis, and model reliability documentation. |
| 9 | Sit-to-stand | Added a second exercise analyzer with its own movement phases, repetitions, and coaching rules. |
| 10 | Session history | Added local database persistence, saved sessions, API access, and history UI. |
| 11 | Therapist dashboard | Added therapist-facing session summaries and review foundations. |
| 12 | Deployment hardening | Added health/readiness behavior, environment validation, artifact controls, and mobile-ready API behavior. |
| 13 | Authentication and privacy | Added users, roles, JWT access, protected endpoints, SecureStore-compatible client behavior, and privacy foundations. |
| 14 | ML/DL expansion architecture | Defined multi-exercise dataset, feature, model registry, training, evaluation, and promotion boundaries. |
| 15 | Exercise dataset adapters | Added normalized adapters for exercise-specific data sources and label mappings. |
| 16A | Exercise recognition foundation | Added experimental multi-class recognition interfaces and candidate-model workflows. |
| 17 | Knee extension | Added knee-extension analysis, tests, API registration, and frontend support. |
| 18 | Shoulder abduction | Added shoulder-abduction analysis, tests, API registration, and frontend support. |
| 19 | Hip abduction | Added hip-abduction analysis, tests, API registration, and frontend support. |
| 20 | Multi-exercise web UX | Unified exercise metadata, library, analyzer selection, results behavior, and mobile preparation across supported exercises. |
| 21 | Expo mobile MVP | Added the React Native/Expo client, authentication flow, exercise library, video picker, uploads, results, and SecureStore tokens. |
| 22 | Mobile QA and cloud preparation | Added device-testing plans, network configuration, deployment checklists, and broader automated mobile coverage. |
| 23 | Controlled staging | Prepared staging Docker/environment configuration and private frontend/backend deployment instructions. |
| 24 | Private staging and pilot gate | Hardened test isolation, readiness checks, EAS profiles, and internal pilot requirements. |
| 25 | Pilot feedback loop | Added internal test scripts, tester onboarding, feedback structure, and reliability boundaries. |
| 26 | Stability candidate | Prevented duplicate submissions, improved retry/cancel/error behavior, and hardened result parsing. |
| 27 | Closed-beta readiness | Consolidated privacy, support, tester, distribution, and go/no-go evidence for controlled external testing. |
| 28 | Launch-candidate fixes | Added stricter staging configuration, known-limitations access, release checks, and candidate documentation. |
| 29 | Invite-only beta execution | Prepared first-wave tester, monitoring, issue-triage, evidence, and release communication assets. |
| 29B / 29E | External tester gates | Separated operational execution evidence from engineering readiness and reviewed the first-wave gate. |
| 30 | Beta results review | Defined the review gate for real tester evidence, reliability findings, and next-wave decisions. |
| 31 | Second-wave preparation | Prepared follow-up release evidence while retaining physical-device, privacy, and distribution gates. |

## Current continuation

Work after the numbered sprint sequence has focused on converting the engineering candidate into a clearer product experience:

- Adopted exercise-coaching features and pose datasets without retaining the source project's name in the product.
- Trained and registered XGBoost and bidirectional GRU temporal recognition candidates.
- Added video-based exercise identification beside manual exercise selection.
- Preserved the selected recognition video when opening analysis, removing the duplicate-upload step.
- Added coach/bystander subject-switch detection and safer single-person guidance.
- Connected the mobile staging build to the deployed Render backend.
- Added the Movena Android icon, adaptive icon, favicon, and splash assets.
- Redesigned the mobile application around Home, Analyze, Exercises, History, and More navigation.
- Reorganized optional analysis artifacts under a collapsed settings menu.
- Added a four-step Exercise → Video → Review → Results progress model.

## Detailed sprint records

The detailed evidence remains in the existing sprint documents, including:

- [Sprint 1–5 review](sprint_1_5_review_report.md)
- [Sprint 10 sessions and history](sprint_10_sessions_database_history.md)
- [Sprint 11 therapist dashboard](sprint_11_therapist_dashboard_mvp.md)
- [Sprint 14 ML/DL expansion](sprint_14_multi_dataset_ml_dl_expansion.md)
- [Sprint 15 dataset adapters](sprint_15_dataset_adapters.md)
- [Sprint 16A recognition foundation](sprint_16a_exercise_recognition_foundation.md)
- [Sprint 17 knee extension](sprint_17_knee_extension_analyzer.md)
- [Sprint 18 shoulder abduction](sprint_18_shoulder_abduction_analyzer.md)
- [Sprint 19 hip abduction](sprint_19_hip_abduction_analyzer.md)
- [Sprint 20 multi-exercise UX](sprint_20_multi_exercise_ui_mobile_prep.md)
- [Sprint 21 mobile MVP](sprint_21_mobile_app_mvp.md)
- [Sprint 22 mobile and cloud preparation](sprint_22_mobile_qa_cloud_prep.md)
- [Sprint 24 private staging](sprint_24_private_staging_deployment.md)
- [Sprint 25 internal pilot](sprint_25_limited_internal_pilot_feedback_loop.md)
- [Sprint 27 closed-beta readiness](sprint_27_external_closed_beta_readiness.md)
- [Sprint 28 launch-candidate fixes](sprint_28_external_beta_launch_candidate_fixes.md)
- [Sprint 29 beta execution](sprint_29_invite_only_external_beta_execution.md)

## Historical interpretation

Sprint labels describe engineering milestones, not clinical validation or public-release approval. Current capabilities and commands should always be taken from the root and mobile READMEs rather than copied from an older sprint record.
