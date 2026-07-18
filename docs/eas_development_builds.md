# EAS Development Builds

`mobile/eas.json` defines internal `development` and `preview` profiles plus a production placeholder. No public store submission is configured. The development profile includes Expo Dev Client and produces an internal Android APK.

```powershell
npm install -g eas-cli
cd mobile
eas login
eas build:configure
eas build --profile development --platform android
```

For iOS, an Apple developer account and signing access are required: `eas build --profile development --platform ios`. Run `npx expo start --dev-client` after installing a development build.

`EXPO_PUBLIC_*` values are embedded in the client and are never secrets. Put only the public API base URL and non-sensitive app mode there. Keep signing credentials, backend `SECRET_KEY`, database credentials, and service tokens in EAS/backend secret stores, never `.env` committed to Git. Use separate internal preview and eventual production API origins.

Limitations: EAS login, project linking, signing, and cloud build were not executed in the current environment because they require project-owner credentials. A successful build does not approve public distribution, real patient data, or clinical use.
