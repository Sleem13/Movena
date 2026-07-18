# Mobile Staging Configuration

## Sprint 24 build status

EAS account/project authentication is available, but the `preview` environment contains no variables and no staging backend URL exists. `preview-staging` build submission is intentionally blocked until `EXPO_PUBLIC_API_BASE_URL` is set to the real private staging API. See `android_internal_build_report.md`.

Mobile analysis remains entirely backend-side. JWTs remain in Expo SecureStore; manual exercise selection and rule-based analysis remain primary.

For local LAN development, use `mobile/.env` with the computer's LAN URL. For controlled staging, register the public staging API URL in EAS's `preview` environment and use the internal `preview-staging` profile:

```powershell
cd mobile
eas env:create --name EXPO_PUBLIC_API_BASE_URL --value https://staging-api.example.com --environment preview --visibility plaintext
eas env:list --environment preview
eas build --profile preview-staging --platform android
```

The profile sets `EXPO_PUBLIC_APP_ENV=staging`, selects EAS `preview` variables, and produces an internal APK. An iOS internal build requires Apple signing access:

```powershell
eas build --profile preview-staging --platform ios
```

`EXPO_PUBLIC_*` variables are public application configuration, not secret storage. Never place backend secrets or database credentials in them. Do not submit either build to an app store. Validate API reachability, authentication, camera/picker, upload interruption, rejected results, SecureStore expiry handling, and signed report/overlay links on a physical device.
