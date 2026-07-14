# PhysioVision AI Product Vision

## Product Direction

PhysioVision AI is intended to become a physiotherapy-informed movement-analysis and rehabilitation-support platform. The bodyweight Squat Analyzer is the first production-shaped vertical slice: it proves video capture, pose extraction, validity gating, confidence communication, movement metrics, visual feedback, and therapist-readable reporting. It is the MVP, not the final product.

The product supports exercise monitoring and structured review. It does not diagnose conditions, prescribe treatment, replace examination by a licensed professional, or claim clinical effectiveness.

## Target Users

- **Patients and exercise participants:** record an assigned movement, receive understandable educational observations, and share a session report.
- **Physiotherapists:** review sessions, measurement quality, movement trends, and patient-reported context while retaining clinical judgment.
- **Clinics:** coordinate programs, governance, retention, and audit policies after identity, consent, and access controls exist.
- **Students and researchers:** inspect transparent biomechanics, confidence, dataset provenance, and experimental model comparisons without treating outputs as clinical truth.

## Product Modules

1. **Patient app:** guidance, capture/upload, results, safety notices, history, and sharing.
2. **Therapist dashboard:** patient queues, session review, exercise plans, annotations, and exports.
3. **Exercise analysis engine:** shared pose/signal infrastructure plus exercise-specific validity, metrics, rules, feedback, and schemas.
4. **Session history:** consent-aware storage of session metadata, results, media references, and trends.
5. **Report generation:** patient-friendly and therapist-readable artifacts with limitations and provenance.
6. **Dataset/model management:** versioned datasets, mappings, evaluation evidence, model status, and rollback.
7. **Safety/confidence layer:** input validity, pose quality, measurement confidence, conservative language, and escalation guidance.

## Product Principles

- Rule-based biomechanics remains primary until stronger evidence supports another role.
- Every exercise is independently validated; adding an endpoint is not proof of safety or usefulness.
- Confidence and limitations are first-class outputs, never hidden behind a score.
- Web ships first. Mobile reuses the backend before on-device analysis is considered.
- Privacy, consent, deletion, provenance, and least-privilege access are architectural requirements.
- Product metrics distinguish usability, engineering reliability, and clinical research evidence.

