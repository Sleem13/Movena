# Sprint 28 - External Beta Launch Candidate Fixes

## Outcome

`0.28.0-rc.1` is prepared as an engineering launch candidate with fail-closed mobile staging configuration, visible beta/limitations copy, privacy-safer upload logging, release/build/QA/retention artifacts, and expanded beta summarization. The external issue log remains empty; no tester result was fabricated.

Supported exercises remain bodyweight squat, sit-to-stand, knee extension, shoulder abduction, and hip abduction. Rule-based analyzers remain primary. ML/DL and recognition remain experimental. There is no on-device analysis, new exercise, public release, patient onboarding, clinical claim, or real patient-identifiable data use.

## Decision

**NO-GO - fix blockers first.** The build registry truthfully records the Android candidate as `blocked_not_submitted`. Private HTTPS staging, EAS build/install, physical-device QA, deployed auth/artifact/retention verification, active support/deletion/feedback links, and approvals remain outstanding.

## Validation result

- Python 3.12.10: 195 tests passed; 7 dependency deprecation warnings.
- Mobile: 61 tests passed; TypeScript `--noEmit` passed.
- Frontend: 33 tests passed; Vite production build passed.
- Artifact cleanup dry-run: 0 expired files and 0 bytes eligible.
- External feedback summary: 0 sessions, 1 blocked/not-submitted build, `NO-GO`.

## Commands

```powershell
python scripts/cleanup_artifacts.py --dry-run
python scripts/summarize_external_beta_feedback.py
python -m pytest

cd mobile
npm test
npm run typecheck

cd ..\frontend
npm test
npm run build
```

Do not run EAS until `EXPO_PUBLIC_API_BASE_URL` is a reviewed private HTTPS URL. Then build with `eas build --profile preview-staging --platform android` and update the registry with the real build evidence.
