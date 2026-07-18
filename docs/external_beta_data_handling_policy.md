# External Beta Data Handling Policy

## Data boundary

Any future external beta is invite-only and non-public. It permits only tester-owned non-identifying exercise test videos and approved synthetic/project fixtures. No real patient video, protected/sensitive health information, name, contact detail, record number, diagnosis, bystander identity, or other unnecessary personal data is allowed.

The beta service may process the test video, pose landmarks/angles, analysis status/confidence/feedback, temporary overlay/report artifacts, account/security metadata needed for access, and privacy-safe operational/feedback records. It is not medical-record infrastructure. Raw video content, diagnosis information, precise location, raw tokens, secrets, and unnecessary request bodies must not enter analytics or issue logs.

## Retention and deletion

Uploads should be temporary and removed after processing. Generated artifacts are designed to expire under configuration (currently up to 24 hours); signed/access-controlled links are not permission to share them. Feedback/issue/build/QA metadata should be retained only through the beta evaluation and approved closeout window. Before `GO`, verify actual storage, cleanup jobs, backups, provider logs, and deletion behavior in staging; record the approved periods rather than relying on this design statement. See `external_beta_data_retention_cleanup_plan.md`.

Testers may request access revocation and deletion of eligible beta data at `[DELETION/PRIVACY CONTACT]`. The owner must authenticate the request without collecting excess identity data, locate scoped records, document exceptions, confirm completion, and avoid promising deletion from systems not yet verified.

## Access and artifacts

Use least privilege, named accounts, strong secrets, HTTPS, explicit CORS, protected endpoints, expiring artifact access, and environment separation. Only authorized beta operations, security/privacy, and engineering personnel with a QA need may review privacy-safe logs or debug data. Test video/artifact review requires explicit need, approved channel, and minimum duration; it must never be copied into general chat or issue trackers.

For a suspected privacy incident: stop affected testing, restrict/revoke access, preserve minimum safe evidence, notify the privacy/security escalation owner, assess containment/deletion/notification obligations, communicate through the private incident channel, remediate, and require a new go/no-go decision. Do not conceal, casually forward, or independently investigate identifiable material.
