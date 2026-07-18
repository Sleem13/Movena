# Internal Pilot Issue Tracking

The source of truth is `data/processed/pilot/internal_pilot_issue_log.csv`. Use the documented categories only: `mobile_ui`, `upload`, `backend_api`, `analysis_result`, `rejected_result`, `auth_token`, `camera_permission`, `network`, `artifact_report_overlay`, `privacy_security`, `safety_copy`, or `documentation`.

Severity values are `blocker`, `high`, `medium`, `low`, and `safety_privacy`. A blocker or safety/privacy issue stops the affected test immediately and requires the pilot, privacy, or safety owner to triage it. High issues block the next build unless explicitly risk-accepted. Medium and low issues need an owner and disposition.

Workflow statuses are `new`, `triaged`, `in_progress`, `blocked`, `fixed`, `wont_fix`, `needs_more_info`, and `closed`. Closure requires reproduction evidence, fixed version, regression result, and reviewer approval. `wont_fix` requires documented rationale.

Write sanitized reproduction steps and safe error codes. Never paste raw tokens, credentials, signed artifact URLs, raw request bodies, patient data, diagnoses, or media into the log. Mark only whether sanitized logs or voluntarily shared evidence are available, and keep restricted evidence outside the CSV.
