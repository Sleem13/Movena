# Sprint 22 — Mobile QA and Cloud Deployment Preparation

## Outcome

Engineering hardening is implemented: standardized errors, cancel/retry, double-submit prevention, local file validation, retained retry context, explicit permission states, selected-video metadata, safe rejected/error results, SecureStore expiry handling, EAS internal profiles, and deployment/privacy QA documentation.

Automated coverage verifies endpoint mappings, all requested error families, token clearing, upload-state guards, five-exercise camera guidance, and no fake score for rejected/error/null-score results. Existing backend behavior and analyzer/ML logic are unchanged.

## Validation record

- Python 3.12.10: `python -m pytest` — 170 passed, 7 dependency deprecation warnings.
- Mobile: `npm test` — 7 suites and 39 tests passed; `npm run typecheck` passed.
- Expo: dependency check passed, public config resolved, and an Android production bundle exported successfully.
- LAN-mode FastAPI smoke: bound to `0.0.0.0:8010`; `/health` returned `ok`; `/api/v1/exercises` returned 12 entries including 5 supported.
- EAS signed cloud build and physical Android/iOS execution: not run; credentials/hardware were unavailable.

## Release decision

Sprint 22 is **conditionally complete**. Code/configuration/documentation acceptance is complete, but at least one physical Android development-build test and EAS signed-build evidence are pending because no physical device or project-owner EAS credentials were available in this environment. No public release is authorized.

## Boundaries and next gate

Analysis remains backend-side, manual exercise selection and rule-based analyzers remain primary, and ML/DL/recognition remain experimental. Sprint 23 should execute the physical-device matrix, close signing/environment setup, validate real upload interruption and token expiry, and conduct a pre-release privacy/security review before any limited external pilot.
