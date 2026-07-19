# Private Beta Link Activation Plan

## Current status

All destinations remain inactive placeholders. No tester invitation or beta activity is authorized. Links must be private, access-tested, staffed, and approved; do not substitute unrestricted public forms. No real patient data, clinical use, diagnosis, or treatment content is permitted.

| Function | Canonical placeholder | Status | Activation evidence required |
|---|---|---|---|
| Feedback form | `[PRIVATE_FEEDBACK_FORM_URL]` | Inactive | Private form opens, submission reaches assigned owner, no health-data fields, access/revocation tested |
| Issue report | `[PRIVATE_ISSUE_REPORT_URL]` | Inactive | Private intake works, severity/privacy flags route correctly, attachments restricted |
| Tester support | `[PRIVATE_SUPPORT_CONTACT]` | Inactive | Named primary/backup, staffed hours, acknowledgement test, outage template ready |
| Privacy/deletion request | `[PRIVATE_DATA_REQUEST_URL]` | Inactive | Request reaches privacy owner, identity-minimizing workflow and closure notification tested |
| Incident report | `[PRIVATE_INCIDENT_CONTACT]` | Inactive | Critical alert reaches security/privacy/safety owners and pause authority is confirmed |
| Consent/privacy notice | `[CONSENT_PRIVACY_URL]` | Inactive | Approved version is read-only, versioned, accessible, and consent tracker references it |
| Known limitations | `[KNOWN_LIMITATIONS_URL]` | Inactive | Approved non-clinical limitations are readable without public beta access |
| Android install | `[PRIVATE_ANDROID_INSTALL_URL]` | Inactive | EAS internal link is restricted, installed on approved device, revocation tested |
| Status/outage | `[PRIVATE_STATUS_URL]` | Inactive | Restricted status notice reaches testers without exposing infrastructure details |

## Activation workflow

1. Assign accountable primary and backup owners for feedback, support, privacy, incident response, and release control.
2. Create destinations in an organization-approved private system with least-privilege access.
3. Remove fields that request names, diagnosis, symptoms, patient data, raw media, tokens, or secrets.
4. Test each link from a non-owner account using synthetic text only.
5. Confirm receipt, triage, response, export/retention, deletion, access revocation, and backup-owner coverage.
6. Replace the canonical placeholders in the tester pack and invite package only after approval.
7. Record URL ownership and activation evidence in a restricted operational registry; do not commit private addresses or credentials if repository visibility is broader than the beta team.
8. Re-run the GO/NO-GO review. Any inactive critical link remains NO-GO.

## Stop conditions

Disable affected links and pause invitations for unintended public access, real patient data submission, unauthorized recipients, missing incident routing, unstaffed support, or inability to honor deletion requests.
