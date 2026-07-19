# EAS Staging Environment Setup

## Current status

EAS authentication succeeds and the preview environment now contains `EXPO_PUBLIC_API_BASE_URL=https://name-physiovision-api-staging.onrender.com` plus `EXPO_PUBLIC_APP_ENV=staging`. A post-fix internal Android rebuild is in progress under build ID `a10a3920-23e3-4097-ae7a-861a61bda01d`.

`EXPO_PUBLIC_*` values are embedded public client configuration. Never place secrets, database credentials, tokens, or private keys in them.

## Preconditions

- [ ] Private Render HTTPS backend is reachable.
- [ ] `/health`, `/ready`, and `/api/v1/exercises` pass against the real staging origin.
- [ ] The backend uses exact HTTPS CORS, authenticated analysis, and disabled public demo mode.
- [ ] The URL is not localhost, a LAN HTTP address, or `.example.invalid`.

## Configure preview environment

From `mobile/`:

```powershell
eas whoami
eas env:create --name EXPO_PUBLIC_API_BASE_URL --value https://<staging-backend-url> --environment preview --visibility plaintext
eas env:create --name EXPO_PUBLIC_APP_ENV --value staging --environment preview --visibility plaintext
eas env:list --environment preview
```

Confirm both variable names and the real HTTPS API origin. The checked-in `preview-staging` profile also fixes `EXPO_PUBLIC_APP_ENV=staging`; the EAS variable makes the preview environment explicit and auditable.

If a variable already exists, use the EAS dashboard or `eas env:update` rather than creating a duplicate. Do not use output flags that reveal sensitive values.

## Build only after staging passes

```powershell
eas build --profile preview-staging --platform android
```

Record the EAS build ID, app version `0.28.0`, release candidate `0.28.0-rc.1`, internal install URL, commit, timestamp, and known limitations. This is internal distribution only—no public app-store release.

Install on a named physical Android device and execute `physical_device_validation_matrix.md`. Revoke the install link/build access if the candidate is rejected or access changes.

Official reference: [Expo EAS environment variables](https://docs.expo.dev/eas/environment-variables/manage/).
