# External Closed Beta Scope

## Purpose and boundary

Sprint 27 prepares an invite-only product-quality beta; it does not authorize distribution. The beta may evaluate installation, upload reliability, result clarity, rejected-result guidance, temporary artifacts, and support workflows. It does not evaluate clinical validity, diagnostic accuracy, treatment effectiveness, or patient outcomes.

The proposed run is 14 calendar days with 8–12 individually invited, controlled testers after every release gate passes. Access must be revocable, builds must not be publicly listed, and participants must acknowledge the consent, privacy, safety, and limitations text before testing.

## Participants

Eligible testers are adults invited by the product team who can follow the test protocol, use their own non-identifying test recordings, and report product observations. Appropriate groups include software QA reviewers, product reviewers, and physiotherapy-domain reviewers acting outside patient care.

Exclude minors, patients testing as part of care, people seeking diagnosis or treatment advice, anyone unable to consent, and anyone planning to upload another person's identifiable video or health information.

## Supported test scope

- `bodyweight_squat`
- `sit_to_stand`
- `knee_extension`
- `shoulder_abduction`
- `hip_abduction`

Allowed inputs are newly recorded tester-owned videos with a neutral background and no identifying documents, bystanders, patient information, audio disclosures, or sensitive health details; approved synthetic/project fixtures may also be used. Unsupported exercises, real patient videos, clinical assessments, injury diagnosis, treatment prescription, emergency use, and medical decision-making are out of scope.

## Success criteria

- All deployment and release-candidate gates pass with evidence.
- Invited testers can install, authenticate, select an exercise, upload, understand success/rejected/error outcomes, and submit feedback.
- No blocker/high safety or privacy issue remains open.
- Upload/retry and token lifecycle work across the approved device matrix.
- Testers see and understand the non-clinical limitation and no-patient-data warnings.
- Feedback contains no patient-identifiable data and is sufficient for a documented next-build decision.

## Stop criteria

Pause access and triage immediately for a suspected privacy incident, public artifact exposure, unsafe or diagnostic copy, serious auth/token failure, repeated launch/upload crashes, consistently unavailable backend, fake scores on rejected input, or repeated misunderstanding of clinical limitations. The beta lead may also stop the run when safe support coverage or revocation capability is unavailable.

## Current authorization

**NO-GO.** Private staging, an installable beta build, deployed smoke testing, and physical-device approval are not evidenced. This document is preparation, not an invitation or launch approval.
