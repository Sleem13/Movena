# External Beta Issue Tracking

The canonical import/export template is `data/processed/beta/external_beta_issue_log.csv`. Use a generated issue ID and tester alias. Never copy patient media, names, health information, raw authorization headers, tokens, secrets, exact private URLs with credentials, or unnecessary logs into the tracker.

Tester-facing issue path: `[PRIVATE ISSUE LINK — REQUIRED BEFORE GO]`; restricted privacy/safety escalation: `[PRIVATE INCIDENT CONTACT]`.

Allowed categories are `mobile_ui`, `upload`, `backend_api`, `analysis_result`, `rejected_result`, `auth_token`, `camera_permission`, `network`, `artifact_report_overlay`, `privacy_security`, `safety_copy`, `onboarding`, and `documentation`. Severity values are defined in the support/escalation plan. Recommended status values are `new`, `triaged`, `in_progress`, `verification`, `resolved`, `deferred`, and `closed`.

Each actionable issue should contain privacy-safe reproduction steps, expected/actual behavior, environment/build, an owner, and resolution evidence. For auth issues, describe the lifecycle stage without recording a token. For analysis issues, use an approved synthetic/test fixture or explain the behavior without attaching personal video. Privacy/safety issues go to the restricted incident channel first; the general issue record should contain only the minimum safe reference.

At each triage, deduplicate, confirm severity, assign ownership, identify affected builds, and decide whether the beta must pause. Closure requires verification on the fixed build and `fixed_in_version`; reopening is allowed when the behavior recurs.
