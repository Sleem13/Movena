# External Beta Feedback Collection — Live Protocol

> Future invite-only beta product QA only. No public release, real patient data, clinical use, diagnosis, or treatment claims. Invitations remain blocked until the pre-invite gate records GO.

## Status and boundary

**Inactive while pre-invite decision is NO-GO.** Use `data/processed/beta/external_beta_feedback_template.csv` only for real, consented testers after GO. It currently has headers only.

Collect product-QA feedback using an alias: device/OS/build/environment, supported exercise, approved video source category, upload/analysis status, rejected-result clarity, result/confidence/camera-guidance clarity, disclaimer/limitations visibility, issue description, severity, privacy/safety flag, and improvement suggestion.

Do not collect names, contact details, real patient media, diagnoses, symptoms, treatment information, health outcomes, raw tokens, secrets, or public artifact links. Do not treat empty feedback or positive responses as clinical evidence.

## Live handling

1. Confirm consent before accepting a response.
2. Validate that exercise, tester alias, build, and environment match the assignment.
3. Remove/quarantine unexpected identifying content under the privacy incident process; do not copy it into ordinary trackers.
4. Route technical issues into the issue log without duplicating sensitive evidence.
5. Mark `privacy_safety_concern=yes` for any possible exposure, unsafe wording, fake score, or misunderstanding of product limitations.
6. Acknowledge through the private staffed channel and record follow-up status.
7. Generate monitoring reports only from genuine rows.

Pause immediately for a real patient-identifiable upload, privacy/security incident, diagnostic wording, public artifact exposure, fake score on rejection, majority upload failure, or launch crash.
