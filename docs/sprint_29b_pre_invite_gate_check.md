# Sprint 29B Pre-Invite Gate Check

## Decision

**NO-GO — fix blockers first. Do not invite testers.** Reviewed 2026-07-19 for release candidate `0.28.0-rc.1`.

This gate applies to a future small, invite-only external beta only. It is not a public release, clinical service, diagnostic tool, or treatment system. No real patients, patient-identifiable recordings, sensitive health data, unsupported exercises, or promoted ML/DL outputs are permitted.

## Evidence

| Required gate | Status | Evidence / blocker |
|---|---|---|
| Backend staging URL works | Pass | Render HTTPS staging responded directly |
| `/health` passes | Pass | HTTP 200; staging, database OK, auth required, public demo disabled |
| `/ready` passes | Pass | HTTP 200; database connection OK and artifact directories writable |
| `/api/v1/exercises` passes | Pass | HTTP 200; five supported exercises and planned exercises unavailable |
| Unauthenticated analysis denied | Pass | Squat analysis without authentication returned HTTP 401 |
| Unapproved origin denied CORS | Pass | No `Access-Control-Allow-Origin` returned for an unapproved origin |
| Current Android build link works | Blocked | Post-auth-fix build `a10a3920-23e3-4097-ae7a-861a61bda01d` is still in progress; previous build is not accepted as post-fix device evidence |
| App installs on Android | Blocked | No connected/named physical Android device or installation record |
| App opens | Blocked | No physical-device execution |
| Safety disclaimer visible | Blocked | Source/tests pass; no physical-device evidence |
| Auth/create demo account works | Blocked | 65 mobile tests pass, including warning isolation; no staging-device account flow |
| Exercise library loads | Blocked | Server endpoint passes; no installed-app evidence |
| Video picker works | Blocked | No physical-device execution |
| Upload flow works | Blocked | No physical-device valid upload |
| Invalid/static input is rejected safely | Blocked | Automated behavior exists; no device/staging evidence |
| Rejected result has no fake score | Blocked | Automated behavior exists; no device/staging evidence |
| Feedback form active | Blocked | `[PRIVATE_FEEDBACK_FORM_URL]` is an inactive placeholder |
| Issue report active | Blocked | `[PRIVATE_ISSUE_REPORT_URL]` is an inactive placeholder |
| Support contact active | Blocked | `[PRIVATE_SUPPORT_CONTACT]` is inactive and unstaffed |
| Privacy/deletion request active | Blocked | `[PRIVATE_DATA_REQUEST_URL]` is inactive and untested |
| Consent/limitations text ready | Partial | Draft text exists; approved active URLs and accountable sign-off are absent |
| Final privacy/safety sign-off | Blocked | No named accountable approval record |

## Required closure

Finish the post-fix build, install it on a named Android device, execute every required physical-device scenario, activate and access-test all private links, verify consent/limitations on device, record privacy/security and healthcare-safety approvals, then repeat this gate review.

Because the decision is NO-GO, no tester invitation, roster entry, consent record, assignment, or beta session may be created.
