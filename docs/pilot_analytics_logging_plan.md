# Pilot Analytics and Logging Plan

No third-party or invasive analytics is implemented for Sprint 25. Structured feedback and sanitized operational logs are sufficient until a privacy owner approves retention, access, notice, deletion, and identifier behavior.

An approved future implementation may emit only: `app_opened`, `exercise_library_loaded`, `exercise_selected`, `camera_guidance_viewed`, `upload_started`, `upload_succeeded`, `upload_failed`, `analysis_success`, `analysis_rejected`, `analysis_error`, and `feedback_submitted`.

Allowed metadata is limited to app version, platform, supported exercise ID, safe status/error code, coarse duration bucket, and coarse network type when available. A tester alias may be supplied only explicitly; do not silently derive identity or use advertising/device identifiers.

Never collect raw video/audio, landmarks, filenames, report/overlay URLs, query strings, names, patient identifiers, diagnoses, free-text health data, precise location, JWTs, credentials, secrets, or raw request bodies. Logs must redact authorization headers and signed artifact parameters. Access must be least-privilege, time-limited, and auditable.

Pilot analytics measures product reliability and clarity only. It cannot be used for clinical decisions, model training, model promotion, or clinical-validation claims without a separate approved governance process.
