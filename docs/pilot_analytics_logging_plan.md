# Pilot Analytics and Logging Plan

No third-party analytics is implemented in Sprint 24. If approved later, collect only app/backend version, platform, exercise selected, upload started/succeeded/failed, analysis status (`success`, `rejected`, `error`), standardized error code, and coarse duration bucket.

Never collect video/audio content, landmarks, report/overlay URLs, filenames, names, emails, patient identifiers, JWTs, credentials, precise location, free-text health information, or raw request bodies. Use randomized installation/session identifiers only after privacy review, document retention and access, aggregate reporting, deletion, opt-out/notice requirements, and validate that logs redact query strings.

Application logs should contain operational event names and safe error codes, not secrets or user content. Access must be least-privilege and time-limited. Analytics cannot be used for clinical decisions or model training without a separate approved governance process.
