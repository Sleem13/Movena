# Native replacement builds

Use Flutter 3.47.4 / Dart 3.13.3. Install Android SDK/JDK for Android, or Xcode on
macOS for iOS. Local tests do not prove camera behavior on a physical device.

Local Android compilation passed with JDK 17, SDK 35/36, NDK 28.2.13676358,
CMake 3.22.1 and Gradle 9.3.1. The Gradle distribution is checksum-pinned.
The APK is `build/app/outputs/flutter-apk/app-debug.apk` (about 188 MiB).
Its configured API is `http://10.0.2.2:8020`, the Android emulator host alias.
Rebuild with a reachable API for a physical device; that address alone does not
run a backend. The debug APK passed signature/package checks, but was not installed.

```sh
flutter pub get
flutter analyze
flutter test
flutter run --dart-define=MOVENA_API_URL=http://10.0.2.2:8020
flutter build apk --debug --dart-define=MOVENA_API_URL=http://10.0.2.2:8020
python ../../scripts/verify_rebuild_android.py
```

Physical devices need a reachable development API origin. Release builds require
an explicitly configured HTTPS `MOVENA_API_URL`. Unmigrated workspaces can open the
existing website when `MOVENA_LEGACY_WEB_URL` is configured with its HTTPS origin.

Production Android identity is `ai.movena.mobile`; debug uses
`ai.movena.mobile.development` so it does not replace an installed signed build.
Release signing requires the existing keystore, through `MOVENA_ANDROID_KEYSTORE`,
`MOVENA_ANDROID_STORE_PASSWORD`, `MOVENA_ANDROID_KEY_ALIAS`, and
`MOVENA_ANDROID_KEY_PASSWORD`. Never commit the keystore or passwords. The release
Gradle task refuses the template's debug-signing fallback.

Pass `--build-number` greater than the most recent installed/distributed Android
version code. Obtain and verify the original EAS signing certificate before any
upgrade test. The existing Expo/EAS project has not been deleted or modified.

iOS retains `ai.movena.mobile`; distribution still requires the original Apple
team/signing setup on macOS. The camera capture uses `enableAudio: false` and does
not request microphone access. Gallery video selection uses the system picker.

The CI workflow is configured for Android debug and iOS simulator compilation;
it has not yet been run. Signed upgrades, camera,
permissions, background/resume and real-device playback remain separate gates.

Account links use `app_links` with Flutter's default deep-link routing disabled.
Both platform manifests register the retained `movena` scheme. Accepted routes are
`movena://verify-email?token=...` and `movena://reset-password?token=...`; forms
require an explicit submit action. Tokens are held in memory and never logged.
Widget tests cover links while signed out and while session restoration is pending.
They also cover returning to login from a link opened while signed in.
OS dispatch, cold launches and signed installation upgrades still require devices.
Email HTTPS origins and associated-domain/universal-link configuration have not
been changed; deployment must connect those links to the approved replacement.

Patient registration currently preserves the existing backend's terms/privacy
consent versions. Configure approved policy documents before public cutover.

Android backup rules include only `FlutterSharedPreferences.xml`, which this app
uses for locale/theme choices. Secure storage, captured media and other files are
excluded from both cloud backup and device transfer. A restored installation must
log in again. This follows the Android [backup inclusion rules](https://developer.android.com/identity/data/autobackup)
and avoids restoring encrypted tokens without their device keystore keys.
Keep health records out of these preferences. Device restore remains unverified.

The merged Android manifest removes the camera plugin's microphone permission;
capture already sets `enableAudio: false`. Camera hardware is optional so devices
without a camera can still select existing videos and use care workflows.
