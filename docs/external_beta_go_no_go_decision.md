# External Beta Go/No-Go Decision

> Sprint 29E execution review (2026-07-19): **NO-GO for invitations.** The internal Android build exists, but real private-link values, accountable approval, physical-device acceptance evidence, and tester/consent records are absent. “Considered active/passed” without verifiable values is not release evidence.

> Sprint 31 readiness review (2026-07-19): **NO-GO — do not invite a second wave.** Sprint 30 has no genuine first-wave results; P0/P1 evidence, installed-build/device-QA, active-link, consent-hosting, and accountable safety/privacy gates remain unresolved.

> Sprint 30 result gate (2026-07-19): **NO-GO / blocked**. All five required beta inputs are header-only. Continue Sprint 29B; zero recorded issues or failures are not positive safety or reliability evidence, and beta expansion is prohibited.

> Sprint 29B pre-invite review (2026-07-19): **NO-GO — do not invite testers.** Render HTTPS, Supabase-backed health/readiness, auth enforcement, and exercise metadata pass. The post-fix build is unfinished/uninstalled, physical-device QA is unexecuted, private links are inactive, and privacy/safety sign-off is absent.

> Sprint 28 review: decision remains `NO-GO`. See `external_beta_launch_candidate_go_no_go.md` for `0.28.0-rc.1` evidence.

> Sprint 29 status: execution assets are being prepared, but actual external beta has not started and remains blocked. There are no invited testers, consent records, assignments, feedback, issues, or beta results.

## Decision

**NO-GO — fix blockers first** (reviewed 2026-07-19).

Sprint 27 creates the readiness package but does not prove runtime operations. No public launch, app-store listing, invitation, or patient use is authorized.

## Blocking evidence

- Post-fix Android build completion and physical installation are not recorded.
- No approved physical-device matrix demonstrating launch, login, upload/retry, rejected result, artifact, and logout behavior.
- Token lifecycle, artifact authorization/expiration/cleanup, retention/deletion, and access revocation are not verified in the deployed environment.
- Support, privacy/deletion, feedback, install, and login placeholders have no active owner/channel evidence.
- Feedback, issue, support, privacy/deletion, incident, consent, and limitations destinations remain inactive placeholders.
- No external feedback exists; the empty summary appropriately reports `not_started` and `NO-GO`.

## Criteria to change to GO

All release-candidate checklist items must pass. There must be no open blocker/high safety or privacy issue; backend and private mobile install must be stable; physical Android upload and rejected-result clarity must pass; auth/token and artifact controls must work; privacy/safety text and limitations must be visible and understood; and the feedback/escalation loop must be staffed and tested.

Automatic no-go conditions include a privacy/security blocker, public artifact exposure, serious auth/token flaw, launch crash, consistent upload failure, a normal/fake score on rejected movement, diagnostic interpretation risk, or uncontrolled real-patient-data handling.

The accountable product, security/privacy, safety, QA, and release owners must sign the evidence record. A future `CONDITIONAL GO` may limit devices, testers, features, duration, or artifacts, but cannot waive safety/privacy critical or blocker controls.
