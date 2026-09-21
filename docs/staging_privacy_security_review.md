# Staging Privacy and Security Review

> Historical evidence: provider names and deployment status below describe earlier work.
> For the current AWS-only deployment, use [the deployment guide](aws_api_routing.md).

Sprint 24 status: **blocked before deployment**. No provider/database secrets were configured, no staging URL or APK exists, and no physical device was tested. This avoids claiming closure from local tests alone.

- [x] Staging scope is internal and prohibits real patient-identifiable data.
- [x] Staging startup rejects the default/short secret, wildcard or non-HTTPS CORS, unauthenticated analysis, and public demo mode.
- [x] Mobile tokens use SecureStore and clear on invalid/expired token.
- [x] Upload types/sizes are validated and rejected results show no fake score.
- [x] Local artifact retention is documented; cleanup supports dry-run.
- [x] Protected artifacts require authentication or an expiring HMAC-signed link.
- [x] Rule-based analyzers remain primary; no model was promoted.
- [x] Product copy remains non-diagnostic and non-prescriptive.
- [ ] Provider `SECRET_KEY`, database credential, and exact CORS origins are configured and independently reviewed.
- [ ] Staging HTTPS, database TLS/backups, monitoring, rate limits, and scheduled cleanup are verified.
- [ ] Physical Android QA and signed-link expiry/authorization tests pass against deployed staging.
- [ ] Consent language and privacy policy are approved before any external tester.
- [ ] Private object storage and auditable deletion replace local artifacts before patient-data consideration.
- [ ] AWS services are provisioned with restricted team access and HTTPS.
- [ ] EAS preview API variable, Android build access, and named physical-device test are reviewed.
- [ ] Draft internal safety consent receives organizational privacy/safety approval.

External pilot and real patient use remain blocked while any required unchecked item remains.
