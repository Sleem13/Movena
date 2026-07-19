# Sprint 30 Regression Test Plan

This plan becomes actionable only after verified beta findings exist. Until then, existing automated validation remains required and Sprint 30 is blocked.

## Baseline suites

- Backend: `python -m pytest`
- Mobile: `cd mobile; npm test`
- Frontend: `cd frontend; npm test; npm run build`
- Beta evidence: run monitoring, feedback summary, and results review scripts.

## Required scenarios

- Upload retry after a recoverable failure.
- Request timeout and backend-offline handling.
- Invalid/static input rejection with no fake score and `movement_score=null`.
- Expired token, permission denied, and logout/login behavior.
- Unsupported file rejection.
- Missing, expired, or unauthorized report/overlay artifact.
- Safety disclaimer visibility.
- Known-limitations link visibility and navigation.

## Finding-specific regression

For each genuine issue, record affected build, environment, device, exercise, steps, expected/actual behavior, severity, privacy/safety relevance, owner, fix version, and a focused automated or physical-device test. Recheck valid upload, invalid/static rejection, no fake score, retry/network behavior, auth/token expiry, artifact access/expiry, disclaimers, limitations, and active private support/privacy links.

No beta expansion occurs while blocker/high or safety/privacy findings remain unresolved.
