# Internal Pilot Test Script

Run only after the readiness gate is approved, using controlled non-identifying test media.

| Step | Action | Expected result |
|---|---|---|
| 1 | Install the recorded internal Android build. | Build installs from the restricted link and version matches the registry. |
| 2 | Open the app. | App starts without exposing configuration or debug secrets. |
| 3 | Review the safety screen/disclaimer. | Educational-only, no-diagnosis, stop-exercise, and no-patient-data messages are visible. |
| 4 | Load the Exercise Library. | Exactly five supported analyzers are selectable; planned exercises remain disabled. |
| 5 | Open each supported exercise. | Correct name, description, and camera guidance load without claiming clinical validation. |
| 6 | Review camera guidance. | View, visibility, lighting, stability, and repetition guidance are clear. |
| 7 | Upload/record one controlled video for at least two exercises. | Upload reaches the staging API and returns success, rejected, or a safe structured error. |
| 8 | Upload one invalid/static test video. | Result is rejected, no normal movement score appears, and corrective capture guidance is clear. |
| 9 | Read the rejected result. | Tester can explain why it was rejected and understands it is not a diagnosis. |
| 10 | Turn Wi-Fi off during upload, when safe. | App shows a non-technical network failure, leaks no token/data, and retains a safe retry path. |
| 11 | Restore Wi-Fi and retry. | Retry uses the selected exercise/video and does not double-submit. |
| 12 | Log out/in when auth is enabled. | Secure token behavior works; expired/invalid tokens request login without exposing token content. |
| 13 | Submit feedback and log issues. | Structured rows contain aliases and sanitized QA details only. |

Stop immediately for privacy exposure, auth bypass, missing disclaimer, diagnostic/treatment claims, or a normal score on clearly invalid movement. Record the build, device, backend environment, and safe reproduction evidence.
