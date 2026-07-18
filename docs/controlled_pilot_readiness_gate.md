# Controlled Pilot Readiness Gate

**Decision: external pilot is not approved.** A deployed staging URL or successful internal build does not change this decision.

Approval requires all of the following evidence:

- Staging backend/web/mobile smoke tests pass with exact versions recorded.
- Android physical-device QA passes; iOS is tested or its limitation and exclusion are formally approved.
- Authentication, ownership, token expiry/logout, and role behavior are validated.
- Reports, overlays, uploads, retention, cleanup, and deletion remain private and auditable.
- Privacy/security review, threat review, monitoring, backup/restore, and incident response are complete.
- Consent language, privacy policy, tester instructions, support/escalation, and known limitations are finalized.
- No real patient data is used without explicit organizational/legal/privacy approval.
- A qualified professional reviews product safety language and intended-use boundaries if required.
- No diagnosis, treatment prescription, model promotion, or recognition-first routing is introduced.

The release owner must record a signed go/no-go decision. Silence, partial completion, or engineering readiness is a no-go.
