# External Beta Launch Candidate Release Notes

## Candidate identity

- Release candidate: `0.28.0-rc.1`
- Mobile version: `0.28.0`
- Backend version: `0.28.0` when `APP_VERSION` is applied
- Web package version: `0.1.0`
- Platform/profile: Android APK, EAS `preview-staging`
- Staging environment: **not configured/deployed**
- Build status: **blocked, not submitted**
- Go/no-go: **NO-GO - fix blockers first**

This is an engineering launch candidate, not a public release, distributable binary, or clinical product.

## Supported scope

Bodyweight squat, sit-to-stand, knee extension, shoulder abduction, and hip abduction only. Backend rule-based analyzers remain primary. ML/DL and exercise recognition remain experimental; no analysis runs on device.

## Candidate fixes

- Fail-closed mobile staging/production API URL validation.
- Invite-only/not-public launch-candidate label.
- In-app known-limitations screen and navigation from onboarding/library/results.
- Privacy-safe squat upload logging without source filename.
- Build registry, QA matrix, retention report, invite package, and summary build evidence.

## Known blockers and limitations

Private HTTPS staging, EAS preview configuration, actual APK build/install, physical-device QA, deployed auth/artifact/cleanup verification, legal/privacy approval, and real support/feedback/deletion contacts remain blocked. Camera conditions and pose estimation affect accuracy; rejected results are not clinical findings; scores are not clinical scores; artifacts are temporary; results may be inaccurate.

Local candidate validation passed 195 Python tests, 61 mobile tests plus TypeScript, and 33 frontend tests plus the production build. These results do not replace staging or physical-device evidence.

## Installation (after approval only)

1. Configure `EXPO_PUBLIC_API_BASE_URL` in the EAS preview environment to the reviewed private HTTPS backend.
2. Verify staging `/health`, `/ready`, authentication, CORS, exercises, analysis, and artifacts.
3. Run `eas build --profile preview-staging --platform android` from `mobile/`.
4. Record the EAS build ID/checksum/private URL in the build registry, then install only on approved tester devices.

Do not use the current placeholder URL and do not share a package publicly.

## Rollback and support

Pause invitations, revoke affected beta accounts/links, disable the build or staging service, restore the last verified configuration, and communicate through `[PRIVATE STATUS CHANNEL]`. Preserve only minimum privacy-safe evidence. Support/escalation: `[BETA SUPPORT CONTACT]`; privacy/safety: `[PRIVATE INCIDENT CONTACT]`. These placeholders are release blockers.
