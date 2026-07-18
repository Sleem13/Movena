# Sprint 28 Launch Candidate Fix Plan

## Starting decision

Sprint 27 recorded **NO-GO - fix blockers first**. The feedback and issue CSVs contain no submitted external-beta rows, so there are no participant findings to resolve and no evidence that absence of reports means absence of risk.

## Findings and required actions

| Area | Current finding | Priority | Launch-candidate action | Exit evidence |
|---|---|---:|---|---|
| Privacy/security | Deployment controls are designed but not verified in private HTTPS staging | Blocker | Deploy with strong secret, explicit HTTPS CORS, auth-required analysis, private artifacts, and no public demo | Deployment smoke/security record |
| Android build | `preview-staging` exists but has no real staging API value or installed artifact | Blocker | Configure reviewed EAS preview URL, build private APK, register artifact, install on approved devices | EAS artifact/build ID and device evidence |
| Physical QA | Upload, retry, interruption, permissions, token, result, and artifact paths are automation-only | Blocker | Execute the final QA matrix on physical Android | Signed device matrix |
| Support/onboarding | Install, login, feedback, issue, support, and deletion placeholders are unresolved | Blocker | Assign owners and replace/test every private link/contact | Owner/link verification |
| Retention | 24-hour artifact design and cleanup command exist; deployed scheduling is unverified | High | Verify storage locations, dry-run, cleanup schedule, provider logs/backups, and deletion request flow | Cleanup/deletion evidence |
| Mobile remote configuration | Staging could otherwise fall back to a development URL | High | Fail closed unless staging/production receives a real HTTPS non-placeholder API URL | Unit tests and TypeScript pass |
| Known limitations | No dedicated in-app destination | High | Add a limitations screen linked from onboarding, library, and results | Mobile source/tests |
| Privacy-safe logging | Squat request log included the source filename | High | Log content type only; never log source filename/token/media | Python regression test |
| Rejected scoring | Fake score is a no-go condition | High | Retain validity gate and mobile score suppression; retest all exercises | Backend/mobile tests and device QA |
| Documentation | Sprint 27 drafts exist but RC version/evidence was not assembled | High | Produce release notes, registry, QA matrix, invite pack, retention report, and decision | Versioned Sprint 28 package |

## Scope and sequencing

1. Land code-level fail-closed, copy/navigation, and logging fixes.
2. Run cleanup dry-run and all automated suites.
3. Assemble `0.28.0-rc.1` evidence without claiming an EAS build exists.
4. Deploy private staging and replace placeholders under accountable owners.
5. Build/install private Android APK and execute physical QA.
6. Reassess risks and record a new multi-owner decision.

No public launch, patient onboarding, real patient-identifiable data, new exercise, on-device analysis, model promotion, or clinical claim is part of this plan.
