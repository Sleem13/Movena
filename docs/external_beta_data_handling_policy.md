# External Beta Data Handling Policy

## Sprint 29E execution rule

Create records only from real invited aliases and completed consent. Do not prefill acceptance, consent, assignments, feedback, issues, safety outcomes, or results. The current trackers remain empty, so no first-wave data processing or Sprint 30 review is authorized.

## Sprint 29C collection gate

No first-wave data collection is authorized. Consent, feedback, issue, support, privacy/deletion, incident, and known-limitations destinations remain inactive or unverified; the roster, consent, and assignment trackers remain header-only. Add a real alias only after GO/CONDITIONAL GO, record consent before assignment, and never collect full names, health information, real patient media, diagnosis, or treatment data.

> Sprint 29B status: no external testing or data collection has started. Roster, consent, assignment, feedback, and issue trackers remain header-only. Do not create records until a real tester is privately selected after GO; never prefill consent or results.

> Sprint 29 execution assets are being prepared, but actual external beta has not started and remains blocked. The roster, consent, assignments, feedback, and issues must remain header-only until launch gates and consent are satisfied.

## Data boundary

Any future external beta is invite-only and non-public. It permits only tester-owned non-identifying exercise test videos and approved synthetic/project fixtures. No real patient video, protected/sensitive health information, name, contact detail, record number, diagnosis, bystander identity, or other unnecessary personal data is allowed.

The beta service may process the test video, pose landmarks/angles, analysis status/confidence/feedback, temporary overlay/report artifacts, account/security metadata needed for access, and privacy-safe operational/feedback records. It is not medical-record infrastructure. Raw video content, diagnosis information, precise location, raw tokens, secrets, and unnecessary request bodies must not enter analytics or issue logs.

## Retention and deletion

Uploads should be temporary and removed after processing. Generated artifacts are designed to expire under configuration (currently up to 24 hours); signed/access-controlled links are not permission to share them. Feedback/issue/build/QA metadata should be retained only through the beta evaluation and approved closeout window. Before `GO`, verify actual storage, cleanup jobs, backups, provider logs, and deletion behavior in staging; record the approved periods rather than relying on this design statement. See `external_beta_data_retention_cleanup_plan.md`.

Testers may request access revocation and deletion of eligible beta data at `[PRIVATE_DATA_REQUEST_URL]`. The owner must authenticate the request without collecting excess identity data, locate scoped records, document exceptions, confirm completion, and avoid promising deletion from systems not yet verified.

The canonical placeholder is `[PRIVATE_DATA_REQUEST_URL]`; it is currently inactive. Before `GO`, replace it with an access-controlled request path, verify receipt by the privacy owner and backup, test identity-minimizing request handling and closure notification, and document provider-specific backup/log limitations. `[PRIVATE_FEEDBACK_FORM_URL]`, `[PRIVATE_ISSUE_REPORT_URL]`, and `[PRIVATE_SUPPORT_CONTACT]` are also inactive and must not be presented as working channels.

## Access and artifacts

Use least privilege, named accounts, strong secrets, HTTPS, explicit CORS, protected endpoints, expiring artifact access, and environment separation. Only authorized beta operations, security/privacy, and engineering personnel with a QA need may review privacy-safe logs or debug data. Test video/artifact review requires explicit need, approved channel, and minimum duration; it must never be copied into general chat or issue trackers.

For a suspected privacy incident: stop affected testing, restrict/revoke access, preserve minimum safe evidence, notify the privacy/security escalation owner, assess containment/deletion/notification obligations, communicate through the private incident channel, remediate, and require a new go/no-go decision. Do not conceal, casually forward, or independently investigate identifiable material.
