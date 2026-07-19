# Physical-Device Validation Matrix

## Current execution record — 2026-07-19

Physical Android execution is **blocked**: no valid staging API, `preview-staging` APK, install link, named device, device OS, or assigned tester exists. Build: not generated. Backend URL: unavailable. Every row below is pending and must not be inferred from unit tests, web simulation, or local API checks.

When executable, record device model, Android version, app/build identifier, HTTPS backend origin, tester, timestamp, sanitized evidence, pass/fail, and issue ID for every row. Use only approved synthetic or tester-owned non-identifying videos—never real patient data.

| Required Android scenario | Required evidence | Current result | Current blocker |
|---|---|---|---|
| Install internal build | Installed APK opens from approved private EAS link | Blocked / not tested | No EAS build or install link |
| Open app | Cold and warm launch without crash | Blocked / not tested | No installed build/device |
| Safety disclaimer visible | Disclaimer is readable before analysis use | Blocked / not tested | No installed build/device |
| Exercise library loads from staging | HTTPS request succeeds with no localhost traffic | Blocked / not tested | No staging URL/build |
| Five supported exercises visible | Squat, sit-to-stand, knee extension, shoulder abduction, hip abduction shown | Blocked / not tested | No staging URL/build/device |
| Planned exercises disabled | Planned entries cannot start analysis | Blocked / not tested | No installed build/device |
| Video picker works | Permission accept/deny and approved video selection behave safely | Blocked / not tested | No installed build/device |
| Camera works | Permission accept/deny and short controlled recording work | Blocked / not tested | No installed build/device |
| Valid upload works | Non-identifying valid fixture produces expected safe success state | Blocked / not tested | No staging URL/build/device |
| Invalid/static upload rejected | Static/non-movement fixture returns rejected input | Blocked / not tested | No staging URL/build/device |
| Rejected result has no fake score | Rejected UI suppresses movement score and ML prediction | Blocked / not tested | No staging URL/build/device |
| Retry/network failure handled | Timeout, offline, interrupted Wi-Fi, cancel, and retry are understandable | Blocked / not tested | No staging URL/build/device |
| Expired token handled | Expired token clears safely and requires sign-in | Blocked / not tested | No staging account/build/device |
| Logout/login works | Auth-required session ends and restarts correctly | Blocked / not tested | No staging database/account/build |
| Known limitations visible | Limitations and non-clinical wording remain accessible | Blocked / not tested | No installed build/device |
| Feedback/support links visible | Active private feedback, issue, support, privacy/deletion links open correctly | Blocked / not tested | Links are inactive placeholders |
| Report/overlay access | Protected temporary links open and expire without cross-user access | Blocked / not tested | No staging artifacts/account/build |

Repeat across normal network, slow/throttled network, backend offline, interrupted network, and recovery. Verify success, rejected, upload validation, auth error, timeout, and server-unavailable result states. Capture no real patient media or credentials in screenshots/logs.

Automated mobile tests and web simulation do not satisfy this matrix. Android requires an installed `preview-staging` build on a named physical device. iOS is outside the current required Android gate and must not be marked passed without compatible hardware, signing access, and its own executed record.
