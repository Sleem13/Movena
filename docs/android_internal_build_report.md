# Android Internal Build Report

| Field | Result |
|---|---|
| EAS project | `@selim97/physiovision-ai-mobile` |
| Profile | `preview-staging` |
| Command | `eas build --profile preview-staging --platform android` |
| Distribution | Internal APK |
| Status | Blocked before build submission |
| Blocker | EAS preview contains no `EXPO_PUBLIC_API_BASE_URL`; no real staging backend URL exists |
| Artifact/install link | Not generated |
| Installed device/tester | Not available |
| Public store release | Not attempted or approved |

## Gate-closure attempt — 2026-07-19

- `eas whoami` succeeded for account `selim97`, which owns the configured EAS project.
- `eas env:list --environment preview` succeeded and returned **No variables found for this environment**.
- The checked-in `preview-staging` profile sets `EXPO_PUBLIC_APP_ENV=staging` but intentionally does not embed an API URL.
- Because no real private HTTPS staging backend exists and `EXPO_PUBLIC_API_BASE_URL` is absent, `eas build --profile preview-staging --platform android` was **not submitted**. Submitting an installable build that cannot reach the controlled backend would not close the gate.
- App version remains `0.28.0`; release candidate remains `0.28.0-rc.1`. Build URL and install link: not generated.

Remediation: deploy the private backend, run `eas env:create --name EXPO_PUBLIC_API_BASE_URL --value https://<real-staging-api> --environment preview --visibility plaintext`, verify with `eas env:list preview`, then submit the build. Record the EAS build URL only in the internal release record, install on the named Android device, and execute the physical-device matrix. Never substitute localhost or an invalid placeholder merely to obtain a green build.
