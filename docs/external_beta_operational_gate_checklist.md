# External Beta Operational Gate Checklist

## Current decision

**NO-GO.** This checklist records operational evidence; planning documents and passing unit tests do not count as deployed or physical-device passes. Sprint 30 must not start and testers must not be invited while any required gate is incomplete.

| Required gate | Status | Current evidence / required closure |
|---|---|---|
| HTTPS backend deployed | Pass | Render HTTPS staging origin responded on 2026-07-19 |
| PostgreSQL connected over SSL | Pass for live connectivity | Supabase-backed health/readiness report database OK; backup/restore evidence remains pending |
| `GET /health` passes | Pass | HTTP 200; staging, version, database OK, auth required, public demo disabled |
| `GET /ready` passes | Pass | HTTP 200; database connection OK and artifacts writable |
| `GET /api/v1/exercises` passes | Pass | HTTP 200; five supported exercises and planned unavailable entries returned |
| HTTPS CORS/auth safety | Pass for tested controls | Unauthenticated squat analysis returned 401; unapproved origin received no `Access-Control-Allow-Origin`; health reports public demo disabled |
| Android internal build created | In progress | Post-fix build `a10a3920-23e3-4097-ae7a-861a61bda01d` running |
| Android build installed on physical device | Blocked | No build/install link/named device |
| Valid upload tested on device | Blocked | Requires installed build, staging account, and approved non-identifying fixture |
| Invalid/static upload rejected safely | Blocked | Requires device evidence showing rejected status |
| Rejected result has no fake score | Blocked | Requires device evidence showing score and ML output suppressed |
| Retry/network/token/logout tested | Blocked | Requires physical-device matrix and staging account |
| Feedback/support/privacy links active | Blocked | All canonical links are inactive placeholders |
| Consent, limitations, and safety text approved | Blocked | Drafts exist; accountable approval and active URLs absent |
| Privacy/safety sign-off recorded | Blocked | Named accountable approvals absent |
| No real patient data | Pass as boundary only | Trackers contain no beta data; staging/testers must continue using approved non-identifying fixtures |
| No clinical claims | Pass as documentation boundary | Policies prohibit diagnosis/treatment claims; deployed copy still requires review |

## Required sign-off record

Record date, release candidate, commit, staging URLs, database evidence reference, Android build ID, device/model/OS, QA evidence, open blocker/high issues, link activation evidence, and explicit approvals from product/release, QA, security/privacy, and healthcare-safety owners.

Decision rules:

- **GO:** every operational and approval gate passes with no blocker/high safety or privacy issue.
- **CONDITIONAL GO:** only narrowly scoped non-safety limitations remain, with owner, deadline, monitoring, rollback, and explicit accountable approval; staging, database, installed Android build, physical QA, safe rejection, active support/privacy links, and safety/privacy sign-off must still pass.
- **NO-GO:** any required infrastructure, device, safe-result, privacy/support, or sign-off gate is incomplete.

Current result: **NO-GO — beta invitations are not allowed.**
