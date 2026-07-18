# Limited Internal Pilot Scope

## Purpose and status

Sprint 25 evaluates product usability, upload reliability, result/rejection clarity, safety copy, privacy controls, and issue-reporting workflows. It is product QA only—not clinical validation, research, diagnosis, or treatment evaluation. Execution remains **blocked** until private staging, an installable internal build, physical-device QA, named owners, and privacy/security approval pass.

## Participants and duration

Only invited PhysioVision AI engineering, product, QA, and designated physiotherapy-domain reviewers may participate. The planned pilot lasts 10 business days after the readiness gate is approved. Access is named, revocable, and must not be forwarded.

## In scope

- Controlled flows for `bodyweight_squat`, `sit_to_stand`, `knee_extension`, `shoulder_abduction`, and `hip_abduction`.
- Personally created non-identifying test videos, synthetic media, or reviewed project fixtures.
- Android internal build and staging web/backend behavior.
- Upload success/failure, invalid/static-video rejection, result clarity, temporary reports/overlays, auth/token behavior, and safety/privacy messaging.
- Structured feedback and sanitized issue evidence.

## Out of scope

Public distribution, real patients, clinical workflows, diagnosis, treatment or exercise prescription, emergency use, unsupported exercises, on-device analysis, model promotion, and clinical-performance claims are prohibited. Pilot findings must not be published externally without product, privacy, and safety review.

## Data and privacy restrictions

Use test videos only. Do not upload real patient-identifiable videos, patient names, contact details, diagnoses, health records, credentials, tokens, signed artifact URLs, or precise location. Debug media may be shared only voluntarily, explicitly, and through the approved restricted channel; record consent and delete it under the staging retention process.

## Safety disclaimer

PhysioVision AI provides movement-monitoring feedback for educational product testing. It is not a medical device, does not diagnose or prescribe treatment, and does not replace a licensed healthcare professional. Stop activity for pain, dizziness, numbness, chest discomfort, unusual shortness of breath, instability, or unusual discomfort and seek appropriate professional or urgent help.

## Success criteria

- Every approved tester acknowledges the safety/privacy text.
- Core flows complete on the recorded build and supported devices without blocker, safety, or privacy issues.
- Invalid/static inputs show a clear rejection without a normal score.
- Upload, auth, retry, and artifact behavior match the documented contract.
- Feedback and issue records contain no prohibited data.
- All blocker/high and safety/privacy findings are owned and dispositioned.
- A reviewed findings report records continue/fix/not-ready; results are not presented as clinical validation.
