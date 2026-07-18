# Internal Pilot Build Release Notes

## Candidate record

- Mobile version: `0.24.0`
- Backend version: `0.24.0` when supplied through staging `APP_VERSION`
- Web version: `0.24.0` release candidate
- Staging URL: `<blocked-until-private-https-backend-is-deployed>`
- EAS profile: `preview-staging`
- Android status: **blocked**—EAS is linked, but no real HTTPS staging API URL or installable artifact is recorded.
- iOS status: not built or validated; Apple signing/device access is outside this pilot candidate.
- Distribution: internal only; no store submission or public link is authorized.

Supported exercises remain bodyweight squat, sit-to-stand, knee extension, shoulder abduction, and hip abduction. Previous work added fail-closed staging configuration, explicit API origins, signed temporary artifacts, upload retry/error handling, SecureStore tokens, and clear rejected-result behavior.

Known limitations include backend-only analysis, network dependence, temporary artifacts, single-camera 2D pose limitations, no clinical validation, experimental ML/DL/recognition, and absent physical-device evidence. Report bugs using the feedback template and issue log; never include patient data, tokens, secrets, or unrestricted raw media.

The authoritative build record is `data/processed/pilot/pilot_build_registry.csv`. A build may change to `ready_for_pilot` only after staging reachability, install, smoke, physical-device, privacy, and safety gates pass.
