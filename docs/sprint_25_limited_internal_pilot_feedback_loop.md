# Sprint 25 — Limited Internal Pilot and Feedback Loop

## Decision

Sprint 25 is **engineering-prepared but pilot execution is blocked**. Scope, onboarding, consent, test script, structured CSVs, issue workflow, privacy review, analytics design, build registry, readiness checklist, findings template, and deterministic feedback summarization are implemented. This does not mean a pilot was run.

## Boundaries

Internal invited testers, controlled non-identifying videos, and the five current supported exercises only. No public release, real patients, identifiable patient data, clinical diagnosis/treatment use, unsupported exercise expansion, on-device analysis, ML/DL promotion, or clinical-validation claim is authorized.

Rule-based backend analyzers remain primary. Experimental ML/DL and exercise recognition remain subordinate and must not affect pilot acceptance.

## Execution gate

The pilot stays no-go until a private HTTPS backend/database/web environment exists, the `preview-staging` Android build is generated and installed, physical-device and deployed smoke tests pass, safety/privacy copy is verified on-device, named owners approve the checklist, and every blocker from Sprint 24 is closed.

## Commands

```powershell
# From an activated project .venv
python -m pytest
python scripts/summarize_internal_pilot_feedback.py

cd mobile
npm test

cd ..\frontend
npm test
npm run build
```

The empty pilot templates intentionally produce a no-go/no-evidence summary. Only reviewed controlled-session records may change that recommendation.
