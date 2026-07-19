# External Beta Second-Wave Issue Triage Protocol

Tag genuine issues `beta_wave=second` and classify as `safety_privacy`, `blocker`, `high`, `medium`, or `low`.

| Severity | Action |
|---|---|
| safety_privacy | Pause immediately; restrict evidence; notify privacy/safety owners |
| blocker | Pause affected/all testing; assign owner and rollback decision |
| high | Resolve before the next beta build unless formally stopped and risk-reviewed |
| medium | Triage for current or next controlled cycle |
| low | Backlog with reproduction evidence |

Pause the entire wave for real patient data, a privacy incident, public/cross-user artifact exposure, diagnosis wording, a fake rejected score, launch crash, or uploads failing for most testers. Record sanitized reproduction steps, affected build/platform/exercise, owner, resolution, and fix version.

