# Sprint 28 Issue Resolution Report

## External issue input

`external_beta_issue_log.csv` contains only its header. **No external beta issues have been recorded because no external beta has run.** The rows below are checklist findings, not fabricated tester reports.

| Issue ID | Severity | Category | Status before | Fix implemented | Files changed | Verification | Remaining risk |
|---|---|---|---|---|---|---|---|
| CHECK-28-001 | High | mobile configuration | Open | Remote mobile environments now reject missing, HTTP, and `.invalid` API URLs | `mobile/src/config/env.ts`, `runtimeSafety.ts` | Unit tests and TypeScript | Real EAS preview value and installed build remain blocked |
| CHECK-28-002 | High | onboarding/safety copy | Open | Added invite-only/not-public RC label and dedicated known-limitations screen linked from onboarding, library, success, and rejected result | Mobile routes/screens/tests | Static copy/navigation tests | Physical-device readability and active support links remain blocked |
| CHECK-28-003 | High | privacy/security logging | Open | Removed uploaded source filename from squat request log | Squat route and Python test | Regression test | Deployed log-provider/redaction review remains blocked |
| CHECK-28-004 | Blocker | Android build | Blocked | Registered `0.28.0-rc.1` as `blocked_not_submitted`; no build was fabricated | App config, build registry, release notes | Registry inspection | Needs real HTTPS staging URL, EAS build, install, and device QA |
| CHECK-28-005 | Blocker | support/feedback | Blocked | Tester/support documents contain explicit private placeholders and pause/deletion paths | Beta support/tester/feedback docs | Documentation audit | Owners and real private links must be assigned before invitations |

Existing protections retained: upload preflight, timeout/cancel/retry, permission-denied state, token expiry clearing, rejected-result score suppression, protected/expiring artifacts, strict staging CORS/secret/auth checks, and cleanup dry-run. These are automation-backed only until deployed and physically tested.
