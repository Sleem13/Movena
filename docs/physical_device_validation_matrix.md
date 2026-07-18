# Physical-Device Validation Matrix

## Sprint 24 execution record

Physical Android execution is **blocked**: no valid staging API or `preview-staging` APK exists, and no tester device/model/OS was supplied. Build: not generated. Backend URL: not available. Tester/date: not assigned. The rows below remain pending and must not be inferred from automated tests.

Required Android evidence includes install/open/disclaimer, five supported plus disabled planned exercises, permission accept/deny, picker, real recording, metadata, valid/static/unsupported/oversized upload, cancel/retry, interrupted Wi-Fi, timeout/backend offline, login/logout/expired/invalid token with SecureStore clearing, success/rejection/null score, signed artifacts, and safety text. Record pass/fail, device model, OS, app build, backend URL, tester, timestamp, sanitized notes, and issue IDs.

| Scenario | Android LAN | Android staging | iOS LAN | iOS staging |
|---|---:|---:|---:|---:|
| EAS/internal build installs | Pending | Pending | Account/device dependent | Account/device dependent |
| Camera permission accepted/denied | Pending | Pending | Pending if available | Pending if available |
| Video picker and real recording | Pending | Pending | Pending if available | Pending if available |
| Valid and invalid/static upload | Pending | Pending | Pending if available | Pending if available |
| Cancel, interrupted Wi-Fi, timeout, retry | Pending | Pending | Pending if available | Pending if available |
| Expired token and logout/login | Pending | Pending | Pending if available | Pending if available |
| Report/overlay signed links | Pending | Pending | Pending if available | Pending if available |

Repeat across normal network, slow/throttled network, backend offline, interrupted network, and recovery. Verify success, rejected, upload validation, auth error, timeout, and server-unavailable result states. Capture no real patient media or credentials in screenshots/logs.

Automated mobile tests and web simulation do not satisfy this matrix. Android requires an installed EAS development or `preview-staging` build. iOS requires compatible hardware and Apple account/signing access; if unavailable, document it as an explicit pilot limitation rather than marking it passed.
