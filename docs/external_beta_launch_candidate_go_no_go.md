# External Beta Launch Candidate Go/No-Go

## Decision

**NO-GO - fix blockers first** for `0.28.0-rc.1`.

The candidate contains useful code-level hardening and complete readiness artifacts, but no external beta may start. No public release, store listing, invitation, patient onboarding, or real patient-identifiable data use occurred.

## Passing evidence

- Five exercise endpoints, validity/rejection behavior, upload validation, auth contracts, artifacts, and cleanup are automated-test covered.
- Mobile has timeout, cancellation, retry, permission denial, token-expiry handling, score suppression, a known-limitations route, and fail-closed staging API configuration.
- Strict staging secret, HTTPS CORS, auth-required analysis, and public-demo prohibitions remain enforced.
- Consent/privacy, limitations, feedback/issue schemas, support escalation, retention, invite, and rollback drafts exist.

## Blocking evidence

- No private HTTPS staging deployment or deployed smoke/security record.
- No EAS `preview-staging` Android build, install result, or physical-device matrix.
- No deployed artifact exposure/expiry/cleanup or database/token lifecycle verification.
- No active private install, login, feedback, issue, support, privacy/deletion, or status links.
- Legal/privacy review and accountable product, QA, security, safety, and release approvals are absent.
- No external feedback exists; empty templates cannot validate usability or safety.

## Reconsideration gate

GO requires all blocker/high safety and privacy issues closed, private staging reachable, app installed, uploads/rejected results/token lifecycle/artifacts working on approved Android devices, consent/limitations visible, feedback/support staffed, and no public or real-patient-data path. A privacy exposure, serious auth flaw, launch crash, consistent upload failure, rejected-input score, unsafe wording, or missing consent/support remains an automatic no-go.
