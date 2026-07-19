# Android Internal Build Report

| Field | Result |
|---|---|
| EAS project | `@selim97/physiovision-ai-mobile` |
| Profile | `preview-staging` |
| Command | `eas build --profile preview-staging --platform android` |
| Distribution | Internal APK |
| Status | Build finished; physical-device installation pending |
| Blocker | Physical-device installation and QA pending |
| Artifact/install link | Private EAS internal artifact exists for build `a10a3920-23e3-4097-ae7a-861a61bda01d`; do not distribute before GO |
| Installed device/tester | Not available |
| Public store release | Not attempted or approved |

## Sprint 28D rebuild — 2026-07-19

- EAS preview contains `EXPO_PUBLIC_API_BASE_URL=https://name-physiovision-api-staging.onrender.com` and `EXPO_PUBLIC_APP_ENV=staging`.
- Live HTTPS checks returned `200` for `/health`, `/ready`, and `/api/v1/exercises`; health reports staging, database OK, auth-required analysis, and public demo disabled.
- Previous build `45862c87-e43b-4c1d-8eea-d722f5e367bc` finished successfully for version `0.28.0`.
- Post-fix rebuild `a10a3920-23e3-4097-ae7a-861a61bda01d` finished successfully on 2026-07-19 for Android `0.28.0` build version 1.
- No Android/ADB device was detected on the execution workstation. Installation and physical-device QA are not tested.

When the rebuild finishes, record its final status, fingerprint, archive/install URL, and completion time. Install only through internal distribution on a named Android device, then execute the physical-device matrix. A successful cloud build alone does not authorize beta invitations.
