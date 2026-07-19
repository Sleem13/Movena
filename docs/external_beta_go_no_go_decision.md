# External Beta Go/No-Go Decision

> Sprint 28 review: decision remains `NO-GO`. See `external_beta_launch_candidate_go_no_go.md` for `0.28.0-rc.1` evidence.

> Sprint 29 status: execution assets are being prepared, but actual external beta has not started and remains blocked. There are no invited testers, consent records, assignments, feedback, issues, or beta results.

## Decision

**NO-GO — fix blockers first** (2026-07-18).

Sprint 27 creates the readiness package but does not prove runtime operations. No public launch, app-store listing, invitation, or patient use is authorized.

## Blocking evidence

- No deployed private staging backend/web environment with recorded HTTPS smoke results.
- No installable, private Android beta build configured against the verified staging URL.
- No approved physical-device matrix demonstrating launch, login, upload/retry, rejected result, artifact, and logout behavior.
- Token lifecycle, artifact authorization/expiration/cleanup, retention/deletion, and access revocation are not verified in the deployed environment.
- Support, privacy/deletion, feedback, install, and login placeholders have no active owner/channel evidence.
- No external feedback exists; the empty summary appropriately produces `NO-GO`.

## Criteria to change to GO

All release-candidate checklist items must pass. There must be no open blocker/high safety or privacy issue; backend and private mobile install must be stable; physical Android upload and rejected-result clarity must pass; auth/token and artifact controls must work; privacy/safety text and limitations must be visible and understood; and the feedback/escalation loop must be staffed and tested.

Automatic no-go conditions include a privacy/security blocker, public artifact exposure, serious auth/token flaw, launch crash, consistent upload failure, a normal/fake score on rejected movement, diagnostic interpretation risk, or uncontrolled real-patient-data handling.

The accountable product, security/privacy, safety, QA, and release owners must sign the evidence record. A future `CONDITIONAL GO` may limit devices, testers, features, duration, or artifacts, but cannot waive safety/privacy critical or blocker controls.
