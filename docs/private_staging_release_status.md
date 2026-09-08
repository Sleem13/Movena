# Movena — Private Staging Release Status

## Release Status

Decision: GO for private controlled staging release.

Movena is deployed and validated as a private staging product release. It is suitable for internal review, private demos, and controlled non-clinical testing preparation.

## Evidence

- Render backend service: LIVE
- Supabase PostgreSQL: CONNECTED
- Health endpoint: PASSED
- Ready endpoint: PASSED
- Exercises endpoint: PASSED
- Backend tests: 202 passed, 3 skipped
- Mobile tests: 65 passed
- Frontend tests: 33 passed
- Frontend production build: PASSED

## Supported Exercises

- Bodyweight Squat
- Sit to Stand
- Knee Extension
- Shoulder Abduction
- Hip Abduction

## Release Limitations

- Not a public production release.
- Not approved for clinical decision-making.
- Not a diagnostic tool.
- Does not prescribe treatment.
- Does not replace a licensed physiotherapist.
- No real patient data should be used without consent, privacy review, and security controls.
- External validation is deferred, not completed.

## Next Gate

Closed pilot readiness after privacy, consent, monitoring, and support workflows are completed.
