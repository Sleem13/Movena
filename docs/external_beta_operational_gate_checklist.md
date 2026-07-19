# External Beta Operational Gate Checklist

## Current decision

**NO-GO.** This checklist records operational evidence; planning documents and passing unit tests do not count as deployed or physical-device passes. Sprint 30 must not start and testers must not be invited while any required gate is incomplete.

| Required gate | Status | Current evidence / required closure |
|---|---|---|
| HTTPS backend deployed | Blocked | No Render service/domain/credential; deploy and record sanitized HTTPS origin |
| PostgreSQL connected over SSL | Blocked | No Neon database or `DATABASE_URL`; provision, initialize, and verify TLS |
| `GET /health` passes | Blocked | No staging origin; record timestamped HTTPS response with `environment=staging` |
| `GET /ready` passes | Blocked | No staging/database; record database-ready response without secrets |
| `GET /api/v1/exercises` passes | Blocked | No staging origin; verify five supported and planned unavailable entries |
| Exact HTTPS CORS/auth safety | Blocked | Provider values absent; verify no wildcard, auth required, public demo disabled |
| Android internal build created | Blocked | EAS preview has no API URL; configure only after staging passes and build internally |
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
