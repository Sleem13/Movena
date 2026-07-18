# Sprint 27 — External Closed Beta Readiness

## Outcome

The invite-only external beta governance package is prepared: scope, onboarding, consent/privacy draft, limitations, risk register, support/escalation, data policy, feedback/issue templates, non-invasive analytics plan, tester pack, release checklist, automated summary, and go/no-go controls.

The existing app copy was reviewed. Current safety language uses “exercise monitoring,” “observed movement patterns,” “possible compensation,” “limited observed range,” and confidence/recording-quality concepts. It explicitly avoids diagnosis, injury/weakness detection, treatment, clinical validation, and medical-device claims. No app-copy change or beta label was added because no beta build is authorized; links remain clearly marked placeholders in the draft tester materials.

## Scope controls

Supported exercises remain bodyweight squat, sit-to-stand, knee extension, shoulder abduction, and hip abduction. Rule-based analyzers remain primary. ML/DL and exercise recognition remain experimental. There is no on-device analysis, new exercise, public listing, patient onboarding, clinical claim, or real patient-identifiable data use.

## Evidence and decision

The feedback and issue templates are intentionally empty. Running `python scripts/summarize_external_beta_feedback.py` therefore records zero sessions and a `NO-GO` recommendation. Automated tests validate the summarizer without supplying real participant data.

The operational decision is **NO-GO — fix blockers first**. Required evidence still includes private HTTPS staging, a private Android build, physical-device and network QA, deployed auth/token/artifact/retention verification, and live support/deletion/feedback channels. Sprint 27 documentation readiness does not authorize invitations.

Local validation on 2026-07-18 passed: 193 Python tests (7 dependency deprecation warnings), 58 mobile tests, mobile TypeScript checking, 33 frontend tests, and the Vite production build.

## Validation commands

```powershell
python scripts/summarize_external_beta_feedback.py
python -m pytest

cd mobile
npm test
npm run typecheck

cd ..\frontend
npm test
npm run build
```

## Completion interpretation

Sprint 27 is engineering/documentation complete only when the listed artifacts and automated checks pass. External-beta release readiness remains incomplete until every unchecked operational gate is evidenced and the accountable owners replace the recorded `NO-GO` with a signed decision.
