# Internal Pilot Findings Report

## Pilot overview

No internal pilot was executed. Feedback and issue files contain headers only, so this report records engineering preparation and automated stability evidence—not participant findings or clinical validation.

## Participants and devices

- Testers: 0
- Controlled sessions: 0
- Devices: 0
- Physical builds installed: 0

## Exercises tested

No exercise was tested by a pilot participant. Automated coverage remains limited to the five supported analyzers: bodyweight squat, sit-to-stand, knee extension, shoulder abduction, and hip abduction.

## Upload reliability

Automated review verifies file validation, progress, cancellation, retained retry state, timeout/network copy, and same-tick duplicate-submission prevention. Deployed device-to-staging upload and Wi-Fi interruption are blocked.

## Result and rejected-result clarity

Automated behavior suppresses scores for rejected inputs, labels null scores as “Not scored,” preserves zero reps, tolerates null score breakdown, shows reasons/retry/safety guidance, and treats ML not-applicable as non-predictive. No tester comprehension data exists.

## Authentication and token behavior

SecureStore load/save/clear, bearer attachment, invalid/expired-token clearing, expiry messaging, and logout cleanup pass automation. Deployed token expiry/refresh behavior remains unvalidated; no refresh-token flow exists.

## Privacy, security, and safety findings

No incidents are recorded because no sessions occurred. Automated review confirms standardized private artifact 404s, no filesystem path in error bodies, restricted safety wording, and no invasive analytics. Deployed secrets/CORS/artifact authorization and visible installed-build consent remain open gates.

## Issues fixed

Preventive engineering hardening addressed duplicate submit, exercise-specific guidance, artifact-expiry copy, pilot device metrics, and disclaimer consistency. These were code-review findings, not pilot-reported issues.

## Issues remaining

Private staging, APK installation, physical-device QA, real network conditions, deployed artifact playback, iOS, named approvals, and actual structured feedback are missing.

## Recommendation

Decision: **not ready**. Fix execution blockers first. Do not prepare an external closed beta. After deployment/device/privacy approval, run another limited internal cycle and regenerate this report from actual sanitized feedback.
