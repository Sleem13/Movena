# Mobile QA Plan

Sprint 22 validates the Expo mobile client as an internal engineering build. It does not authorize public release, clinical use, or identifiable patient data.

## Device and network matrix

| Target | Required coverage | Current evidence |
|---|---|---|
| Android physical device | Install development build, permissions, pick/record, LAN upload, retry, results | Required manual gate; not executed without a connected device |
| Android emulator | Backend through `10.0.2.2:8010`, picker and API flows | Supported configuration; automated logic tests complete |
| iOS simulator | Picker and API flows if macOS/Xcode is available | Optional; unavailable in the current Windows environment |
| iOS physical device | Signed development build and LAN flow if Apple account/device is available | Optional; not executed |

Run each available target on same-Wi-Fi LAN, backend unavailable, slow network, interrupted upload, expired/invalid token, large video, and unsupported type. Record device model, OS, build identifier, backend commit, network, result, and evidence. VPN, WARP, cellular fallback, and firewall behavior must be noted.

## Exercise and result matrix

Run `bodyweight_squat`, `sit_to_stand`, `knee_extension`, `shoulder_abduction`, and `hip_abduction` through exercise details, camera guidance, selection/recording, upload, and results. For each exercise cover successful analysis, rejected/invalid movement, upload validation error, auth-required response, network failure, safe backend 500, and timeout.

Expected behavior:

- Success shows only backend-returned metrics and optional artifacts.
- Rejection shows no score, explains recording limitations, and retains exercise/video for retry.
- Errors show no stack trace or fake result and allow retry.
- `401`, `INVALID_TOKEN`, and `TOKEN_EXPIRED` clear SecureStore and request login.
- Missing confidence, pose quality, score breakdown, overlay, report, or ML fields render as unavailable or remain hidden.

## Evidence and exit gate

Automated tests cover endpoint mapping, structured errors, token clearing, double-submit prevention, upload validation, five-exercise guidance, and safe result helpers. Sprint 22 release readiness additionally requires at least one Android physical-device pass, a development-build install, real video upload, offline/interrupted upload, and expired-token evidence. Until recorded, physical-device acceptance is pending.
