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

Remediation: deploy the private backend, run `eas env:create --name EXPO_PUBLIC_API_BASE_URL --value https://<real-staging-api> --environment preview --visibility plaintext`, verify with `eas env:list preview`, then submit the build. Record the EAS build URL only in the internal release record, install on the named Android device, and execute the physical-device matrix. Never substitute localhost or an invalid placeholder merely to obtain a green build.
