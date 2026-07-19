# External Beta Support and Escalation

> Sprint 29E execution status: no genuine support, feedback, issue, privacy/deletion, or incident interaction exists. Placeholder destinations are not treated as active; beta execution remains stopped until access and staffing are verified.

## Sprint 29C private-link gate

| Required destination | Status | Evidence gap |
|---|---|---|
| Consent text | Inactive | Approved private URL and consent version not supplied |
| Feedback form | Inactive | Private form, owner, and receipt test absent |
| Issue report | Inactive | Private tracker/form and access test absent |
| Support contact | Inactive | Staffed primary/backup channel absent |
| Privacy/deletion request | Inactive | Approved private workflow and receipt/deletion test absent |
| Incident report | Inactive | Restricted recipient and escalation test absent |
| Known limitations | Blocked | Repository text exists; private tester URL/access test absent |

No placeholder is an active link. First-wave invitations remain prohibited.

> Sprint 31 status: second-wave onboarding remains blocked because the private feedback, issue, support, privacy/deletion, incident, consent, and limitations destinations are inactive or unverified. Do not distribute placeholders or invite testers.

> Sprint 30 result gate: no feedback or issue records exist and no external support outcome can be assessed. Continue Sprint 29B. Do not infer that zero reports means zero incidents; private channels must be activated, staffed, and access-tested before controlled execution.

> Sprint 29B status: all feedback, issue, support, privacy/deletion, incident, consent, and limitations destinations remain inactive. No channel is staffed or approved for live external testing, so invitations are prohibited.

> Sprint 29 execution assets are being prepared, but actual external beta has not started and remains blocked. The placeholders below are inactive release blockers; no invitation or testing is authorized.

Sprint 28D activation audit (2026-07-19): no approved private URLs, support mailbox/channel, incident recipient, privacy/deletion workflow, or accountable primary/backup contacts were supplied. All rows therefore remain inactive; no destination was fabricated from a personal address or public form.

## Channels and coverage

| Function | Controlled placeholder | Status |
|---|---|---|
| Tester support | `[PRIVATE_SUPPORT_CONTACT]` | Inactive — owner/channel not supplied |
| Privacy/safety escalation | `[PRIVATE_INCIDENT_CONTACT]` | Inactive — owner/channel not supplied |
| Beta owner/on-call | `[BETA_OWNER_AND_BACKUP]` | Inactive — staffing not assigned |
| Status/outage notice | `[PRIVATE_STATUS_URL]` | Inactive — URL not supplied |
| Feedback form | `[PRIVATE_FEEDBACK_FORM_URL]` | Inactive — URL not supplied |
| Issue report | `[PRIVATE_ISSUE_REPORT_URL]` | Inactive — URL not supplied |
| Privacy/data deletion request | `[PRIVATE_DATA_REQUEST_URL]` | Inactive — URL not supplied |

These are planning placeholders, not active contacts. Before `GO`, verify access, staffing hours, backup owner, and revocation permissions. Response targets are operational goals, not service-level guarantees: safety/privacy critical—acknowledge within 1 hour during the staffed beta window and pause immediately; blocker—4 staffed hours; high—1 business day; medium—2 business days; low—next triage cycle.

Activation evidence must include a successful privacy-safe submission from a non-tester account, authorized-recipient receipt, access-control review, deletion/escalation routing, backup-owner acknowledgement, and a documented revocation test. Do not replace these with public unrestricted forms.

## Severity

- **Safety/privacy critical:** suspected data exposure, unsafe claim, identifiable patient content, or misuse that could cause harm.
- **Blocker:** launch/login/core testing cannot proceed for multiple testers; no safe workaround.
- **High:** major upload/result/auth/artifact failure affecting core testing, or a misleading outcome with limited exposure.
- **Medium:** material issue with a safe workaround.
- **Low:** cosmetic, documentation, or minor usability issue.

## Triage and escalation

1. Acknowledge without requesting health information, raw tokens, secrets, or patient media.
2. Create an issue using a beta alias; mark privacy/safety status and limit access.
3. For critical/blocker issues, pause invitations and affected access, preserve only necessary privacy-safe evidence, notify the accountable lead, and assess deletion/revocation.
4. Reproduce with synthetic/approved test data, assign an owner, fix/review/test, and record the fixed version.
5. Resume only after the go/no-go owner documents evidence and communicates the outcome.

Pause the beta for any suspected privacy incident, artifact exposure, unsafe/diagnostic copy, repeated test-blocking crashes, serious auth failure, or repeated misunderstanding of clinical limitations. Revoke an individual account through the staging identity/admin procedure; for systemic risk disable invitations or the beta environment. Never distribute account lists in ordinary issue channels.

For an outage, send a short private notice stating affected service, start time, safe tester action (“stop uploads”), next update time, and resolution—without logs, identifiers, speculation, or clinical language.
