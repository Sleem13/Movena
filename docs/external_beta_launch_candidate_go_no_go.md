# External Beta Launch Candidate Go/No-Go

## Private controlled staging release decision

**Decision: GO for private controlled staging release.**

Movena backend and frontend infrastructure are deployed and validated. The system is suitable for private demonstrations, internal review, and controlled non-clinical testing.

### Evidence

- Render backend service is live.
- Supabase PostgreSQL is connected.
- `/health` endpoint passed.
- `/ready` endpoint passed.
- `/api/v1/exercises` endpoint passed.
- Backend validation passed: 202 passed, 3 skipped.
- Mobile validation passed: 65 passed.
- Frontend validation passed: 33 passed.
- Frontend production build passed.

### Release limitations

- Not approved for public production release.
- Not approved for real clinical decision-making.
- Not approved for diagnosis or treatment prescription.
- Does not replace a licensed physiotherapist.
- No real patient data should be used without consent, privacy review, and security controls.
- Real external user validation is deferred, not completed.

This staging decision does not change the external beta decision below. External beta evidence remains intentionally deferred.

## Decision

**NO-GO — fix blockers first** for `0.28.0-rc.1` (reviewed 2026-07-19).

The candidate contains useful code-level hardening and complete readiness artifacts, but no external beta may start. No public release, store listing, invitation, patient onboarding, or real patient-identifiable data use occurred.

## Passing evidence

- Five exercise endpoints, validity/rejection behavior, upload validation, auth contracts, artifacts, and cleanup are automated-test covered.
- Mobile has timeout, cancellation, retry, permission denial, token-expiry handling, score suppression, a known-limitations route, and fail-closed staging API configuration.
- Strict staging secret, HTTPS CORS, auth-required analysis, and public-demo prohibitions remain enforced.
- Consent/privacy, limitations, feedback/issue schemas, support escalation, retention, invite, and rollback drafts exist.

## Blocking evidence

- The post-fix EAS `preview-staging` rebuild is not yet complete and has not been installed on a physical device.
- No physical-device execution record exists for auth, upload, safe rejection, retry/network, token lifecycle, or limitations.
- No deployed artifact exposure/expiry/cleanup or full database backup/restore lifecycle verification exists.
- No active private install, login, feedback, issue, support, privacy/deletion, or status links.
- Legal/privacy review and accountable product, QA, security, safety, and release approvals are absent.
- No external feedback exists; empty templates cannot validate usability or safety.

## Current gate decision

| GO requirement | Evidence | Decision |
|---|---|---|
| HTTPS staging reachable | Render HTTPS returned `200` for `/health`, `/ready`, and `/api/v1/exercises` on 2026-07-19 | Pass |
| Managed PostgreSQL ready | Supabase-backed `/health` reports database OK and `/ready` reports database connection OK | Pass for connectivity; backup/restore evidence still pending |
| Android internal build installed | Post-fix EAS build `a10a3920-23e3-4097-ae7a-861a61bda01d` is in progress; no device installation | Fail |
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
- `mobile\npm test`: 11 suites and 65 tests passed.
- `frontend\npm test`: 4 files and 33 tests passed.
- `frontend\npm run build`: production build passed.

These automated results support code-level regression confidence only. Separate live checks now prove basic HTTPS and database reachability, but neither evidence set proves Android installation, physical-device behavior, link staffing, backup/restore, privacy/legal approval, or external-beta safety/usability.

## Sprint 28D validation — 2026-07-19

- Live staging: `/health`, `/ready`, and `/api/v1/exercises` returned HTTP 200.
- Deployed safety: unauthenticated squat analysis returned HTTP 401; an unapproved origin received no CORS allow-origin header.
- Mobile: 11 suites and 65 tests passed, including auth/upload warning isolation.
- Python: 198 tests passed with 7 dependency deprecation warnings.
- Frontend: 33 tests passed and the production build succeeded.
- Physical Android device: not detected; all device scenarios remain unexecuted.
- Private beta links: inactive placeholders; no privacy/safety operational sign-off recorded.

The decision remains **NO-GO** because successful staging and automated tests do not replace physical-device QA, active private support/privacy channels, or accountable sign-off.

## Reconsideration gate

GO requires all blocker/high safety and privacy issues closed, private staging reachable, app installed, uploads/rejected results/token lifecycle/artifacts working on approved Android devices, consent/limitations visible, feedback/support staffed, and no public or real-patient-data path. A privacy exposure, serious auth flaw, launch crash, consistent upload failure, rejected-input score, unsafe wording, or missing consent/support remains an automatic no-go.
