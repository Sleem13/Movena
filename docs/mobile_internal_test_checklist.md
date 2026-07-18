# Mobile Internal Test Checklist

Record build ID, device/OS, backend version, tester, date, and pass/fail evidence for each step. Use only synthetic or non-identifiable recordings.

1. Install the EAS development build and launch it.
2. Confirm onboarding and safety language appear.
3. Open `/health` from the phone browser using the LAN backend URL.
4. Load the exercise library and confirm five supported exercises plus disabled planned entries.
5. Open every supported exercise and confirm its details.
6. Confirm exercise-specific camera guidance and permission-denied recovery.
7. Pick and upload a valid video; repeat with a camera-recorded video.
8. Upload an invalid/static recording and confirm rejection with no score.
9. Stop the backend before upload; confirm friendly offline handling and retained selection.
10. Interrupt Wi-Fi during upload; confirm cancel/retry and no double submission.
11. Use an expired/invalid token; confirm SecureStore clears and a login message appears.
12. Test oversized, empty where feasible, and unsupported files.
13. Confirm rejected and error results show Try Again with the selected exercise retained.
14. Verify missing overlay/report/confidence fields do not create fake data.
15. Open the safety page and verify non-diagnostic disclaimer and stop guidance.
16. If enabled, verify protected session history ownership and logout/login.
17. Confirm no token, raw media, patient identifier, or stack trace appears in client logs.

Android physical-device execution is a pending Sprint 22 release gate in this workspace. iOS testing is conditional on Apple hardware/account access.
