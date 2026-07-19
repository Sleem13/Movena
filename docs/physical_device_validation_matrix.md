# Physical-Device Validation Matrix

## Internal physical therapist reviewer evidence — 2026-07-19

Physical-device QA is **partially passed at the internal-reviewer level**. A project owner/developer who is a physical therapist reported testing the app, recorded under privacy-safe alias `PT_INTERNAL_001` in `internal_reviewer_qa_log.csv` as `internal_physical_device_qa` with result `partial_pass`.

This is real internal reviewer evidence, not external beta evidence. Device model, Android version, app build, backend environment, exercise, issue outcome, safety/privacy outcome, and scenario-level pass/fail details were not reported and are not inferred. The granular matrix rows below therefore still require evidence. External tester physical-device QA remains pending, and this internal record does not authorize external invitations by itself.

## Sprint 29C gate update — 2026-07-19

EAS build `a10a3920-23e3-4097-ae7a-861a61bda01d` is now `FINISHED` as an internal Android `0.28.0` APK. This closes only the cloud-build step. ADB is unavailable on the current workstation, no named Android device is connected, the APK has not been verified as installed, and no physical scenario below has been executed. Physical-device QA remains **blocked / incomplete**.

## Current execution record — 2026-07-19

Physical Android execution has **partial internal reviewer evidence**, but remains incomplete for release gating. The Render staging API and Supabase-backed readiness checks pass, and the post-fix `preview-staging` build finished. No device/ADB evidence is available on the validation workstation, no scenario-level internal evidence was supplied, and no external assigned device tester has executed the matrix. Every granular row remains pending unless separately evidenced.

When executable, record device model, Android version, app/build identifier, HTTPS backend origin, tester, timestamp, sanitized evidence, pass/fail, and issue ID for every row. Use only approved synthetic or tester-owned non-identifying videos—never real patient data.

| Required Android scenario | Required evidence | Current result | Current blocker |
|---|---|---|---|
| Install internal build | Installed APK opens from approved private EAS link | Blocked / not tested | Build finished; no connected physical device or installation evidence |
| Open app | Cold and warm launch without crash | Blocked / not tested | No installed build/device |
| Safety disclaimer visible | Disclaimer is readable before analysis use | Blocked / not tested | No installed build/device |
| Create demo account warning isolation | Account screen never shows “Select a video before starting analysis” | Blocked / not tested | No installed build/device |
| Invalid email auth validation | Invalid email produces account-only validation | Blocked / not tested | No installed build/device |
| Exercise library loads from staging | HTTPS request succeeds with no localhost traffic | Blocked / not tested | Server endpoint passes; no installed device evidence |
| Five supported exercises visible | Squat, sit-to-stand, knee extension, shoulder abduction, hip abduction shown | Blocked / not tested | No staging URL/build/device |
| Planned exercises disabled | Planned entries cannot start analysis | Blocked / not tested | No installed build/device |
| Video picker works | Permission accept/deny and approved video selection behave safely | Blocked / not tested | No installed build/device |
| Submit without video | Upload screen shows only the select-video warning | Blocked / not tested | No installed build/device |
| Camera works | Permission accept/deny and short controlled recording work | Blocked / not tested | No installed build/device |
| Valid upload works | Non-identifying valid fixture produces expected safe success state | Blocked / not tested | No installed device evidence |
| Invalid/static upload rejected | Static/non-movement fixture returns rejected input | Blocked / not tested | No installed device evidence |
| Rejected result has no fake score | Rejected UI suppresses movement score and ML prediction | Blocked / not tested | No installed device evidence |
| Retry/network failure handled | Timeout, offline, interrupted Wi-Fi, cancel, and retry are understandable | Blocked / not tested | No installed device evidence |
| Expired token handled | Expired token clears safely and requires sign-in | Blocked / not tested | No staging account/build/device |
| Logout/login works | Auth-required session ends and restarts correctly | Blocked / not tested | No installed device/test account evidence |
| Known limitations visible | Limitations and non-clinical wording remain accessible | Blocked / not tested | No installed build/device |
| Feedback/support links visible | Active private feedback, issue, support, privacy/deletion links open correctly | Blocked / not tested | Links are inactive placeholders |
| Report/overlay access | Protected temporary links open and expire without cross-user access | Blocked / not tested | No staging artifacts/account/build |

Repeat across normal network, slow/throttled network, backend offline, interrupted network, and recovery. Verify success, rejected, upload validation, auth error, timeout, and server-unavailable result states. Capture no real patient media or credentials in screenshots/logs.

Automated mobile tests and web simulation do not satisfy this matrix. Android requires an installed `preview-staging` build on a named physical device. iOS is outside the current required Android gate and must not be marked passed without compatible hardware, signing access, and its own executed record.
