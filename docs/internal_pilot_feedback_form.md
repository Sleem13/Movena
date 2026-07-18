# Internal Pilot Feedback Form

Use one row in `data/processed/pilot/internal_pilot_feedback_template.csv` per controlled test session. Use a non-identifying tester alias and `YYYY-MM-DD` date. Do not enter names, emails, diagnoses, patient identifiers, credentials, token values, signed URLs, or raw media.

Record device/OS/build, staging environment, supported exercise, controlled video source, upload outcome, analysis status, rejection clarity, result/score-confidence/camera-guidance clarity, and whether safety messaging was visible. Describe only sanitized product behavior.

Allowed severity values:

- `blocker`: core flow impossible or pilot cannot safely continue.
- `high`: major supported behavior fails repeatedly.
- `medium`: recoverable behavior with material usability impact.
- `low`: minor or cosmetic problem.
- `safety_privacy`: possible unsafe wording, unauthorized data, token/artifact exposure, missing disclaimer, or privacy concern; stop affected testing and escalate immediately.

Set `screenshot_or_video_shared=yes` only after voluntary explicit sharing through the approved restricted channel. Never embed the media or private link in the CSV. Feedback supports product QA, not clinical validation.
