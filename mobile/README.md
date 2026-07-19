# PhysioVision AI Mobile MVP

## Sprint 31 second-wave status

The second external beta wave is **NO-GO / blocked**. The post-fix Android candidate has no verified physical-device installation or QA record, Sprint 30 has no real beta results, and private tester/support/privacy links remain inactive. Do not distribute a second-wave build or invite testers. Mobile continues to support only the five registered exercises and makes no clinical claim.

## Sprint 29 execution status

Sprint 29 execution assets are being prepared, but the actual external beta has not started and remains blocked. Mobile `0.28.0` / RC `0.28.0-rc.1` has no submitted EAS artifact or physical-device approval, and private staging plus active feedback/support/privacy links are unavailable.

Do not invite testers or distribute the app publicly. Use only non-identifying test videos after a future GO decision; never upload real patients or sensitive health information. The app is not for clinical use, diagnosis, treatment, or medical decisions. The five supported exercises, rule-based backend primacy, experimental ML/DL/recognition boundary, and no-on-device-analysis architecture remain unchanged.

## Sprint 28 launch candidate

Mobile version `0.28.0` represents engineering candidate `0.28.0-rc.1`. Staging/production now fails closed unless `EXPO_PUBLIC_API_BASE_URL` is a real HTTPS non-placeholder URL. The app shows an invite-only/not-public label and provides a known-limitations screen from onboarding, the library, and results.

The candidate remains **NO-GO** and no EAS build was submitted. A real private staging URL, APK install, physical-device upload/network/token/artifact QA, and active private support/feedback/deletion links are still required. Never distribute publicly or upload real patients, identifiable personal information, or sensitive health information. The five supported exercises and backend rule-based primacy are unchanged; ML/DL/recognition remain experimental and no analysis runs on device.

```powershell
npm test
npm run typecheck

# Run only after a reviewed private HTTPS URL exists in the EAS preview environment:
eas build --profile preview-staging --platform android
```

## Sprint 27 external closed beta readiness

The mobile client is included in a future invite-only beta plan, but no external build is approved. The decision is **NO-GO** until private HTTPS staging, an installable non-public Android build, physical-device upload/network/token/artifact QA, and active support/privacy contacts are evidenced. Do not distribute through public stores or links.

External testing, if later approved, is limited to tester-owned non-identifying test videos and the five supported exercises. Never upload real patients, identifiable personal information, or sensitive health information. Rule-based backend analysis remains primary; ML/DL and recognition remain experimental, and no analysis runs on device. See the [tester onboarding](../docs/external_tester_onboarding.md), [known limitations](../docs/external_beta_known_limitations.md), and [go/no-go decision](../docs/external_beta_go_no_go_decision.md).

## Sprint 26 stability candidate

Mobile version `0.26.0` prevents same-tick duplicate upload requests, retains retry/cancel behavior, adds exercise-specific camera and rejected-result guidance, handles null/zero/ML-not-applicable result states safely, and maps expired artifacts and processing failures to non-technical messages. Tokens remain in Expo SecureStore and are never logged.

This is an internal automated-test-validated candidate, not a public or installed pilot release. No real patient data is permitted. The five supported exercises are unchanged, backend rule-based analysis remains primary, and ML/DL/recognition remain experimental. Private staging, Android build installation, physical-device QA, and pilot feedback are still blocked.

## Sprint 25 internal pilot status

The mobile client is prepared for a limited internal product-QA pilot, but no pilot build is approved or installed yet. The `preview-staging` build remains blocked until a real private HTTPS backend URL is configured and deployment/device gates pass. Do not distribute publicly, onboard patients, or upload patient-identifiable media.

Pilot testers may use only controlled test videos and the five supported exercises. Rule-based backend analysis remains primary; the app has no on-device pose estimation or ML/DL. Experimental ML/DL and recognition are not clinical features. Feedback reports product reliability and clarity only, not clinical validity. Follow the [tester onboarding](../docs/internal_tester_onboarding.md), [test script](../docs/internal_pilot_test_script.md), and [readiness checklist](../docs/internal_pilot_readiness_checklist.md).

## Sprint 24 Android build status

The EAS project is linked and `preview-staging` is configured for internal APK distribution. Build submission is blocked because the EAS preview environment has no `EXPO_PUBLIC_API_BASE_URL` and no private staging API exists. After deployment, set the real HTTPS URL, run `eas build --profile preview-staging --platform android`, and record/install the artifact internally. No store submission is authorized.

## Sprint 23 internal staging

The `preview-staging` EAS profile is internal-only and reads `EXPO_PUBLIC_API_BASE_URL` from the EAS `preview` environment. Configure it with `eas env:create`, verify with `eas env:list --environment preview`, then run `eas build --profile preview-staging --platform android`. Do not publish the build or place backend secrets in `EXPO_PUBLIC_*` values. See [mobile staging configuration](../docs/mobile_staging_configuration.md).

Expo/React Native TypeScript client for the five supported PhysioVision AI rule-based analyzers. The app performs no on-device pose estimation or ML/DL; videos are uploaded temporarily to FastAPI for backend-side analysis.

Sprint 21 completed the engineering MVP. Sprint 22 prepares internal physical-device QA and cloud deployment; it is not a public release.

## Setup

```powershell
cd mobile
npm install
Copy-Item .env.example .env
npx expo start
```

Set `EXPO_PUBLIC_API_BASE_URL` in `.env`:

- Android emulator: `http://10.0.2.2:8010`
- Physical phone on the same Wi-Fi: `http://192.168.x.x:8010` using the development computer's LAN address
- iOS simulator on the same computer may use `http://127.0.0.1:8010`
- Expo web defaults to `http://127.0.0.1:8010` when no `.env` override is provided

Start FastAPI on the matching LAN-visible host/port, for example `python -m uvicorn app.main:app --host 0.0.0.0 --port 8010` from `backend/`. The phone and computer must share Wi-Fi, the private-network firewall must allow Python/TCP 8010, and VPN/WARP must not block LAN traffic. Never use `localhost` on a physical phone. Configure `CORS_ALLOWED_ORIGINS` explicitly when required; native requests do not use a browser origin, while Expo web does.

## Commands

```powershell
npm test
npm run typecheck
npx expo start
npx expo start --dev-client
```

The project targets Expo SDK 57. Press `a` for an Android emulator or use an SDK 57 development build. During Expo SDK transition periods, the store version of Expo Go may lag the newest SDK; follow the current Expo compatibility guidance before scanning a physical-device QR code.

## Mobile flow

Onboarding → Exercise Library → Exercise Details → Camera Guidance → Video Selection/Recording → Upload → Result. History, login/profile, and safety screens are also included. JWT access tokens are stored with `expo-secure-store`, never AsyncStorage.

Supported exercises are bodyweight squat, sit-to-stand, knee extension, shoulder abduction, and hip abduction. Planned exercises appear disabled. Manual exercise selection and rule-based biomechanics remain primary; exercise recognition and ML/DL remain experimental.

The picker supports existing videos and a camera recording up to 60 seconds where the platform camera honors that setting. The UI displays available metadata, rejects unsupported or oversized files early, reports upload progress, permits cancellation, prevents double submit, retains the selection for retry, parses structured FastAPI errors, and suppresses movement scores for rejected/error input.

## Internal EAS development build

```powershell
npm install -g eas-cli
eas login
eas build:configure
eas build --profile development --platform android
```

`eas.json` contains internal development/preview profiles and a production placeholder only. Do not place secrets in `EXPO_PUBLIC_*` values or commit `.env`. EAS login, project linking, signing, and a physical-device install require owner credentials and remain manual gates.

## Limitations and safety

- Analysis requires network access to a configured FastAPI backend.
- Upload progress covers transfer; backend processing duration depends on video length and CPU.
- Artifacts are temporary and may expire.
- Expired/invalid access tokens are cleared from SecureStore, but auth has no refresh-token or server-side logout revocation flow yet.
- Physical Android/iOS execution is not proven by automated tests; follow the physical-device and internal-test checklists.
- `npm audit` currently reports moderate transitive advisories in Expo CLI/config build tooling. Expo 57 is the current compatible SDK and Expo's checker passes; reassess advisories with each SDK/toolchain patch rather than applying an incompatible forced downgrade.
- This development app is not medical-record infrastructure and must not contain real patient-identifiable information.
- PhysioVision AI supports exercise monitoring and does not replace assessment by a licensed physiotherapist. It does not diagnose, detect injury or weakness, or prescribe treatment.
