# Movena Mobile

Expo/React Native Android client for guided exercise recognition and video-based movement analysis.

## User experience

The application uses five persistent destinations:

- **Home** — one primary entry point for starting an analysis.
- **Analyze** — guided Exercise → Video → Review → Results workflow.
- **Exercises** — supported movement library and manual selection.
- **History** — protected saved-session review.
- **More** — profile, login, safety, privacy, and limitations.

Users may identify an exercise from a short video or choose it manually. A confirmed recognition suggestion carries the same temporary video into analysis, avoiding a second selection or upload.

## Supported analysis workflow

1. Record or choose a short exercise video.
2. Identify the movement automatically or choose it manually.
3. Confirm the exercise.
4. Review the selected video and optional analysis settings.
5. Upload once to the configured FastAPI backend.
6. Review repetitions, movement feedback, confidence, and optional artifacts.

The backend performs pose estimation and movement analysis. No pose model runs on the phone.

## Requirements

- Node.js and npm.
- Expo SDK 57-compatible dependencies from `package-lock.json`.
- Android phone or Android emulator.
- A running backend for local development, or the deployed HTTPS backend for staging builds.
- Expo/EAS account access for signed cloud builds.

## Install dependencies

From the repository root:

```powershell
Set-Location mobile
npm ci
npx expo install --check
```

Use `npm ci` for reproducible builds. Use `npm install` only when intentionally changing dependencies.

## Configure the backend URL

### Physical Android phone with a local backend

Create the mobile environment file:

```powershell
Set-Location mobile
Copy-Item .env.example .env
notepad .env
```

Set the values to the backend computer's LAN IPv4 address:

```dotenv
EXPO_PUBLIC_API_BASE_URL=http://192.168.1.50:8010
EXPO_PUBLIC_APP_ENV=development
```

Replace `192.168.1.50` with the value returned by:

```powershell
Get-NetIPAddress -AddressFamily IPv4 |
  Where-Object { $_.IPAddress -notlike '127.*' -and $_.IPAddress -notlike '169.254.*' } |
  Select-Object InterfaceAlias,IPAddress
```

Start the backend from the repository root:

```powershell
Set-Location backend
..\.venv\Scripts\python.exe -m uvicorn app.main:app --env-file ..\.env --host 0.0.0.0 --port 8010
```

Test from the phone browser before opening the app:

```text
http://192.168.1.50:8010/health
http://192.168.1.50:8010/api/v1/exercises
```

The phone and computer must share Wi-Fi. Do not use `localhost` or `127.0.0.1` on a physical phone because those addresses refer to the phone itself.

### Android emulator with a local backend

Use Android's host-machine alias:

```dotenv
EXPO_PUBLIC_API_BASE_URL=http://10.0.2.2:8010
EXPO_PUBLIC_APP_ENV=development
```

### Deployed staging backend

The `preview-staging` EAS profile currently uses:

```text
https://name-movena-api-staging.onrender.com
```

Verify it before building:

```powershell
Invoke-RestMethod https://name-movena-api-staging.onrender.com/health
Invoke-RestMethod https://name-movena-api-staging.onrender.com/ready
Invoke-RestMethod https://name-movena-api-staging.onrender.com/api/v1/recognition/models
```

## Run the application for development

Start Expo with a clean bundler cache:

```powershell
Set-Location mobile
npx expo start --clear
```

Then choose one of these options:

- Press `a` for an Android emulator.
- Scan the QR code with a compatible development client.
- Run `npx expo start --web` for layout testing. Expo web runs on port `8081` and automatically calls the standard local FastAPI backend at `http://127.0.0.1:8000`; browser CORS rules apply to web but not native Android requests.

For Expo web, start the backend on its standard local port before starting Expo:

```powershell
Set-Location backend
..\.venv\Scripts\python.exe -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

Set `EXPO_PUBLIC_API_BASE_URL` only when the API runs somewhere else. An explicit value always overrides the development default.

For a development-client build:

```powershell
Set-Location mobile
npx expo start --dev-client --clear
```

## Validate before building

Run every command from `mobile/`:

```powershell
npm ci
npx expo install --check
npm run typecheck
npm test -- --runInBand
npx expo export --platform android
```

Do not continue to EAS if TypeScript, tests, dependency checks, or the Android bundle fails.

## Build an installable Android APK

The `preview-staging` profile creates an internally distributed APK, uses the deployed HTTPS backend, includes the Movena icon/splash assets, and automatically increments Android `versionCode`.

### EAS project identity

The existing EAS project is `@selim97/physiovision-ai-mobile`, linked by
`extra.eas.projectId` (`3161d775-09da-468e-b97d-f678ca583c4c`) in `app.json`.
Keep `expo.slug` as `physiovision-ai-mobile` while using that project. The
installed app's display name is controlled separately by `expo.name` (`Movena`).
Changing the local slug during a rebrand without renaming the linked project
causes EAS to stop with `Project config: Slug for project identified by
"extra.eas.projectId" ... does not match the "slug" field ...`.

If this error appears, verify the linked project with `npx eas-cli project:info`
after logging in. Keep its slug and ID aligned; do not create a replacement
project to resolve a display-name change.

After committing and pushing a configuration fix, start a new
`preview-staging.yml` workflow run from the updated `main` commit. Re-running
the old failed run can use the old commit and repeat the error. The EAS GitHub
project base directory for this repository is `mobile`.

Run these exact PowerShell commands manually:

```powershell
Set-Location mobile

npm ci
npx expo install --check
npm run typecheck
npm test -- --runInBand
npx expo export --platform android

npx eas-cli login
npx eas-cli whoami
npx eas-cli build --platform android --profile preview-staging --non-interactive --wait
```

The final command uploads the source to EAS, signs the Android application with the configured remote keystore, waits for completion, and prints the APK installation URL.

To submit the build and return immediately instead of waiting in the terminal:

```powershell
npx eas-cli build --platform android --profile preview-staging --non-interactive --no-wait
```

Check the latest Android build later:

```powershell
npx eas-cli build:list --platform android --limit 1
```

Open the printed EAS build URL on the phone, download the APK, permit installation from that browser when Android asks, and install the application.

## Build a local Android debug APK on Windows

The local Gradle build requires the Android SDK path and Android Studio's bundled JDK. Run the commands in this order:

```powershell
Set-Location mobile

$env:ANDROID_HOME = "$env:LOCALAPPDATA\Android\Sdk"
$env:ANDROID_SDK_ROOT = $env:ANDROID_HOME
$env:JAVA_HOME = "C:\Program Files\Android\Android Studio\jbr"
$env:Path = "$env:JAVA_HOME\bin;$env:ANDROID_HOME\platform-tools;$env:Path"

npm ci
npx expo prebuild --platform android --clean
Set-Content -LiteralPath android\local.properties -Value "sdk.dir=$($env:ANDROID_HOME.Replace('\','/'))"

Set-Location android
.\gradlew.bat assembleDebug --no-daemon
```

The APK is created at:

```text
mobile/android/app/build/outputs/apk/debug/app-debug.apk
```

The `android/` directory is generated native output in this managed Expo project. After copying the APK elsewhere, it can be removed:

```powershell
Set-Location mobile
Remove-Item -LiteralPath android -Recurse -Force
```

## Build a local-network preview APK

The current `preview` profile contains a LAN backend address. Confirm that `mobile/eas.json` contains the current computer IP before running this profile.

```powershell
Set-Location mobile
npx eas-cli build --platform android --profile preview --non-interactive --wait
```

This APK works only while the phone can reach that LAN address and the local backend is running on port `8010`.

## Build a development-client APK

Use this build when native-module debugging or Expo development-client features are required:

```powershell
Set-Location mobile
npx eas-cli build --platform android --profile development --non-interactive --wait
```

After installation, start Metro:

```powershell
npx expo start --dev-client --clear
```

## Build a production Android App Bundle

Google Play uses an Android App Bundle (`.aab`), not the internal APK profile. Before building, configure the production EAS public variables:

```powershell
Set-Location mobile
$env:PHYSIOVISION_PRODUCTION_API = "https://api.movena.ai"
npx eas-cli env:create --environment production --name EXPO_PUBLIC_API_BASE_URL --value $env:PHYSIOVISION_PRODUCTION_API --visibility plaintext
npx eas-cli env:list --environment production
```

Then validate and build:

```powershell
npm ci
npx expo install --check
npm run typecheck
npm test -- --runInBand
npx expo export --platform android
npx eas-cli build --platform android --profile production --non-interactive --wait
```

Replace the staging Render URL with the reviewed production API URL before a real store release.

## Android branding

Brand assets are configured in `app.json`:

```text
assets/images/icon.png
assets/images/adaptive-icon.png
assets/images/splash-icon.png
assets/images/favicon.png
```

After changing any icon, splash screen, native plugin, Android package setting, or permission, create a new native build. Restarting Metro alone does not update installed native assets.

## Build profiles

| Profile | Output/use | Backend |
|---|---|---|
| `development` | Internal development-client APK | Development environment |
| `preview` | Internal LAN-test APK | IP configured in `eas.json` |
| `preview-staging` | Internal installable staging APK | Deployed HTTPS staging API |
| `production` | Store-oriented Android App Bundle | Production EAS environment |

## Common problems

### `Cannot reach Movena`

- Confirm `/health` works from the phone browser.
- Confirm the app was built with the intended `EXPO_PUBLIC_API_BASE_URL`.
- For local testing, keep the phone and computer on the same Wi-Fi.
- Allow Python through Windows Firewall on private networks.
- Disable VPN/WARP temporarily if it blocks LAN traffic.

### Recognition model unavailable

Check:

```powershell
$env:PHYSIOVISION_API = "https://name-movena-api-staging.onrender.com"
Invoke-RestMethod "$env:PHYSIOVISION_API/api/v1/recognition/models"
```

The response must report an available temporal recognition model.

### Camera unavailable

An emulator, desktop browser, or computer without a camera may report this normally. On a phone, verify Android camera permission under **Settings → Apps → Movena → Permissions**. Users can still choose an existing video.

### APK will not update

The installed build and new build must use the same Android package and signing key, and the new build needs a higher `versionCode`. The `preview-staging` and `production` profiles use `autoIncrement`.

### PowerShell blocks npm scripts

Use the command shim without changing machine-wide policy:

```powershell
npm.cmd ci
npm.cmd run typecheck
npm.cmd test -- --runInBand
```

## Security and data handling

- Never place secrets in `EXPO_PUBLIC_*`; these variables are readable in the built client.
- JWT access tokens use Expo SecureStore.
- Videos are uploaded temporarily to the configured backend.
- Artifact URLs may expire.
- Use non-identifying test videos until privacy, consent, retention, and deletion workflows are approved.
- The application is not medical-record infrastructure.

## Safety boundary

Movena supports exercise monitoring and coaching conversations. It does not diagnose conditions, prescribe treatment, replace clinical assessment, or provide emergency guidance. Stop if pain, dizziness, or unusual symptoms occur.

## Related documentation

- [Physical-device testing](../docs/mobile_physical_device_testing.md)
- [Mobile API contract](../docs/mobile_api_contract.md)
- [Mobile staging configuration](../docs/mobile_staging_configuration.md)
- [Internal mobile test checklist](../docs/mobile_internal_test_checklist.md)
- [Development journey](../docs/development_journey.md)
