# External Beta Launch Candidate Go/No-Go

## Decision

**NO-GO — fix blockers first** for `0.28.0-rc.1` (reviewed 2026-07-19).

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

## Current gate decision

| GO requirement | Evidence | Decision |
|---|---|---|
| HTTPS staging reachable | No Render/Vercel URL or provider credentials; deployed smoke endpoints untested | Fail |
| Managed PostgreSQL ready | No Neon credential/database; schema, seed, backup, and restore unexecuted | Fail |
| Android internal build installed | EAS is authenticated, but preview environment has zero variables and no build/install link | Fail |
| Physical-device QA passed | No named Android device or executed matrix | Fail |
| Valid upload and safe rejection | Automated tests only; no deployed-device evidence | Fail |
| Rejected result has no fake score | Automated tests only; no deployed-device evidence | Fail |
| Consent/privacy/safety text ready | Draft content exists; accountable approval and active consent/privacy URL absent | Fail |
| Feedback/support/privacy links active | All controlled placeholders are inactive | Fail |
| No real patient data | Repository/beta trackers contain no beta execution data | Pass as a boundary, not validation |
| No clinical claims | Product policy and draft copy prohibit clinical claims | Pass as a documentation boundary |

Because every operational gate must pass, neither `GO` nor `CONDITIONAL GO` is supportable. **Beta invitations are not allowed.**

## Activation package

The minimum closure workflow is now documented in:

- `operational_staging_activation_plan.md`
- `postgresql_activation_checklist.md`
- `eas_staging_env_setup.md`
- `private_beta_link_activation_plan.md`
- `external_beta_operational_gate_checklist.md`

These documents are execution instructions, not completion evidence. The current checklist contains blocked operational gates, so this decision remains **NO-GO**. Re-review only after real provider, endpoint, database, build, physical-device, private-link, and accountable sign-off evidence is recorded.

## Repository validation — 2026-07-19

- `python -m pytest`: 198 passed, with 7 dependency deprecation warnings.
- `mobile\npm test`: 10 suites and 61 tests passed.
- `frontend\npm test`: 4 files and 33 tests passed.
- `frontend\npm run build`: production build passed.

These results support code-level regression confidence only. They do not prove private HTTPS reachability, PostgreSQL operations, Android installation, physical-device behavior, link staffing, privacy/legal approval, or external-beta safety/usability.

## Reconsideration gate

GO requires all blocker/high safety and privacy issues closed, private staging reachable, app installed, uploads/rejected results/token lifecycle/artifacts working on approved Android devices, consent/limitations visible, feedback/support staffed, and no public or real-patient-data path. A privacy exposure, serious auth flaw, launch crash, consistent upload failure, rejected-input score, unsafe wording, or missing consent/support remains an automatic no-go.
