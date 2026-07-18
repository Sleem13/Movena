# Internal Tester Onboarding

## Before testing

1. Confirm that you are an invited internal tester and acknowledge the pilot safety/consent text.
2. Use test videos only. **Do not upload real patient-identifiable videos.**
3. Install only the Android APK/link and build ID recorded in the pilot build registry. Do not forward it. iOS is not currently validated.
4. If configuration is required, set only the approved HTTPS staging API URL. Never enter a backend secret in the app.
5. Use the assigned staging account when authentication is enabled. If an approved demo build is supplied, use demo mode only as documented. Never share credentials or tokens.

## Core flow

1. Open the app and confirm the safety disclaimer is visible.
2. Confirm the app/build version shown by the release coordinator matches the registry.
3. Load the Exercise Library and select one of the five supported exercises.
4. Review exercise-specific camera guidance: full body/joints visible, stable camera, good lighting, and the instructed view.
5. Record or select a short non-identifying controlled test video. Do not include names, faces where avoidable, documents, screens, or private surroundings.
6. Upload to the approved staging backend and wait for `success`, `rejected`, or `error`.
7. Treat scores and feedback as movement-monitoring product output only. The app provides movement monitoring feedback, not diagnosis.
8. Submit the structured feedback form and use the issue log for reproducible bugs. Use an alias, sanitized logs, and no raw token or signed URL.

Stop testing and notify the pilot owner immediately for unauthorized access, identifiable data exposure, misleading diagnosis/treatment wording, a score on clearly invalid movement, or missing safety copy. Stop exercise for pain, dizziness, numbness, or unusual discomfort. Delete local test recordings when no longer needed and log out after testing.
