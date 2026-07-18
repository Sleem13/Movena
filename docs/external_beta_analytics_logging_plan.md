# External Beta Analytics and Logging Plan

## Status

This is a design-only plan. Sprint 27 does not add third-party analytics or invasive tracking. Implementation requires explicit privacy/security approval, consent behavior, retention limits, environment review, and tests.

## Allowed events

`beta_app_opened`, `beta_consent_viewed`, `beta_consent_accepted`, `exercise_library_loaded`, `exercise_selected`, `camera_guidance_viewed`, `upload_started`, `upload_succeeded`, `upload_failed`, `analysis_success`, `analysis_rejected`, `analysis_error`, `feedback_submitted`, and `logout`.

Allowed metadata is limited to app version, platform, exercise ID, status/error code, coarse duration bucket, network type when available and justified, and tester alias only after explicit consent. Prefer generated event/session IDs, aggregate counts, short retention, access control, and redaction. Do not infer identity by joining device metadata.

## Prohibited content

Never log raw video/audio, image frames, real names, contact details, patient identifiers, diagnoses, symptoms/medical history, free-form health text, raw tokens, credentials/secrets, precise location, or unrestricted request/response bodies. URLs must be sanitized so signed tokens and artifact credentials are not retained.

## Operational controls before implementation

- Approve a purpose, data dictionary, owner, retention/deletion period, access list, and consent version.
- Disable collection until consent; support withdrawal where applicable.
- Verify staging and production separation, encryption, redaction, and least privilege.
- Test event allow-listing and confirm prohibited payloads cannot be emitted.
- Use aggregate beta reporting; do not evaluate clinical effectiveness or participant health.
- Include analytics in the privacy notice and incident process before enabling it.
