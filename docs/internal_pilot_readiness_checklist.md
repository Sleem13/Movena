# Internal Pilot Readiness Checklist

Sprint 26 update: automated stability checks and preventive fixes are complete, but no private deployment, Android installation, physical-device run, tester session, or human approval has occurred. Existing unchecked execution gates remain mandatory for candidate `0.26.0`.

Status: **NO-GO until every required execution item is evidenced for the exact build.**

- [ ] Private HTTPS backend staging is reachable and `/health`/`/ready` pass.
- [ ] Recorded Android internal build is installed on an approved device.
- [ ] Exercise Library loads exactly five supported analyzers.
- [ ] Controlled upload works for at least two supported exercises.
- [ ] Invalid/static video is rejected without a normal score.
- [ ] Auth/token login, expiry, logout, and SecureStore lifecycle pass.
- [ ] Safety disclaimer is visible on onboarding, upload/results, and safety/about surfaces as designed.
- [x] Feedback form CSV is ready.
- [x] Issue log CSV and severity workflow are ready.
- [x] Tester onboarding is ready.
- [x] Privacy/consent text is drafted; final owner approval remains required.
- [x] Known limitations are documented.
- [ ] No-real-patient-data warning is verified on the exact app build.
- [ ] Named pilot, engineering, privacy, security, and safety owners are assigned.
- [ ] Go/no-go decision, date, build IDs, and approvers are recorded.

Automation and documentation cannot satisfy the deployment, installation, device, or human-approval rows. No pilot session may start while a required row is incomplete.
