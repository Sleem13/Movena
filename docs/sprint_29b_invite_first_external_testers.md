# Sprint 29B — Invite First External Testers

## Status

**Not started / NO-GO.** Sprint 29B execution is blocked at the pre-invite gate. No testers have been invited, accepted, consented, assigned, or activated. Feedback and issue logs contain no beta rows. Sprint 30 must not start.

The intended first wave is limited to 3–5 trusted, non-clinical external testers using aliases and non-identifying test videos. It is invite-only, not public or app-store distribution, and not clinical use or validation. No real patients, patient-identifiable data, diagnosis/treatment claims, new exercises, or ML/DL promotion are allowed.

## Supported scope

- `bodyweight_squat`
- `sit_to_stand`
- `knee_extension`
- `shoulder_abduction`
- `hip_abduction`

Planned exercises remain visible only as disabled/unavailable entries.

## Execution order

1. Obtain a GO or narrowly bounded CONDITIONAL GO from the pre-invite gate.
2. Select 3–5 real trusted testers and add aliases only—never names or health data.
3. Send the approved invite privately and obtain versioned consent before assignments.
4. Assign at least two supported exercises plus invalid/static, retry/network, result clarity, rejection clarity, and camera-guidance checks.
5. Staff support, privacy, and incident channels throughout the controlled window.
6. Pause immediately for any stop condition in the live issue protocol.
7. Generate monitoring/check-in reports from real records only.

## Current decision

The execution order stops at step 1. Draft invitation and instruction assets exist, but they must not be sent. The only accurate status is **Sprint 29B incomplete / invitations blocked**.

## Validation — 2026-07-19

- External beta monitoring: passed; status `not_started`, 0 real tester records.
- External beta feedback summary: passed; 0 sessions.
- Python: 198 tests passed with 7 dependency deprecation warnings.
- Mobile: 11 suites and 65 tests passed.
- Frontend: 4 files and 33 tests passed.
- Frontend production build: passed.

Passing automation does not close physical-device, private-link, consent approval, or accountable sign-off gates.
