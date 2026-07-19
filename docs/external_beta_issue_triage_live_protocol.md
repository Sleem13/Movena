# External Beta Issue Triage — Live Protocol

## Status and boundary

**Inactive while pre-invite decision is NO-GO.** Use `data/processed/beta/external_beta_issue_log.csv` only for genuine reports from consented testers or authorized beta operators. No issue rows currently exist.

Allowed severity values:

- `safety_privacy`: suspected exposure, real patient data, unsafe claim, fake rejected score, cross-user access, or public artifact.
- `blocker`: app cannot launch, authenticate, upload, or complete core controlled testing safely.
- `high`: serious core-flow failure or misleading result with limited exposure.
- `medium`: material defect with a safe workaround.
- `low`: cosmetic, documentation, or minor usability issue.

## Triage

1. Acknowledge through the private channel without requesting patient data, health narratives, passwords, tokens, or raw logs.
2. Record alias, platform/device/OS, build, environment, supported exercise, safe reproduction steps, expected/actual behavior, severity, privacy/safety flag, owner, and status.
3. For `safety_privacy` or blocker issues, pause invitations/testing, revoke affected access if necessary, preserve minimum privacy-safe evidence, and notify product/release, QA, security/privacy, and healthcare-safety owners.
4. Reproduce with synthetic or approved non-identifying fixtures.
5. Fix, review, test, record the fixed build, and repeat GO/NO-GO before resuming.

Pause immediately for real patient-identifiable data, privacy/security incident, diagnosis/treatment wording, public artifact exposure, fake score on a rejected result, uploads failing for most testers, or launch crash. Never downgrade a safety/privacy report to meet a schedule.
