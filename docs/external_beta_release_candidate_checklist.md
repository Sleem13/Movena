# External Beta Release Candidate Checklist

Candidate version: `0.28.0-rc.1` (engineering candidate; Android build blocked/not submitted). Date: 2026-07-18.

## Deployment and device evidence

- [ ] Private staging backend deployed and HTTPS health/analyze/auth/artifact smoke tests recorded.
- [ ] Staging web deployed, if included, with correct API/CORS configuration.
- [ ] Private Android beta/internal build available from a non-public channel.
- [x] iOS is documented as unavailable for this candidate; no iOS beta is claimed.
- [ ] Physical-device QA passes on the approved Android matrix.
- [ ] Upload, cancel, retry, timeout, and network interruption QA passes.
- [ ] Login, expiry, logout, revocation, and protected artifact token lifecycle passes.
- [ ] Artifact authorization, expiration, cleanup, preview, and download privacy review passes.

## Product, safety, and operations

- [x] Retention and deletion expectations are documented, pending deployed verification.
- [x] Consent/privacy draft exists, with legal/privacy review marked as required.
- [x] Long and short known-limitations pages exist.
- [x] Support/escalation plan and pause/revocation criteria exist; contact placeholders remain unresolved.
- [x] Feedback and issue templates exist and prohibit patient/health data.
- [x] No-real-patient-data warning and non-clinical product language are documented and present in current mobile safety copy.
- [x] Current code does not promote ML/DL or claim new exercises.
- [x] Mobile staging/production fails closed without a real HTTPS API URL.
- [x] Known limitations are linked from onboarding, library, and results.
- [x] Squat request logs omit the uploaded source filename.
- [ ] All tester-pack placeholders are replaced and links tested.
- [ ] Go/no-go owner records `GO` after reviewing all evidence.

## Automated validation

- [x] Backend Python suite passes: 195 tests on Python 3.12.10 (2026-07-18).
- [x] Mobile passes: 61 tests and TypeScript `--noEmit` (2026-07-18).
- [x] Frontend passes: 33 tests and Vite production build (2026-07-18).

## Recorded decision

**NO-GO — fix blockers first.** Do not invite or distribute. The unchecked deployment, build, physical-device, token, artifact, contact, and final-validation gates are release blockers.
