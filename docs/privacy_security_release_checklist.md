# Privacy and Security Release Checklist

Unchecked items block external or patient-data testing.

Sprint 24 review: repository controls pass, but provider secrets, deployed HTTPS/CORS, private database, Android device QA, consent approval, and privacy policy remain unchecked. Internal pilot start is blocked.

- [x] Development guidance prohibits real patient-identifiable data.
- [x] Mobile JWT uses platform SecureStore and is cleared on logout or invalid/expired-token response.
- [x] Backend secrets and local `.env` files are excluded from source control.
- [x] Upload size and supported video formats are validated by backend; mobile performs an early user-friendly check.
- [x] Rejected movement is not shown as a successful score or ML result.
- [x] Safety copy makes no diagnosis or treatment-prescription claim and includes pain/unusual-symptom guidance.
- [x] Staging templates require analysis auth, disable public demo mode and ML second opinion, and contain no real secret.
- [x] Protected local artifact tests require auth or an unexpired signed link.
- [ ] Production CORS is restricted to deployed exact origins and verified in the deployed environment.
- [ ] Auth/roles are enabled and penetration-tested for every protected resource.
- [ ] Consent text and a versioned consent workflow are approved.
- [ ] Privacy policy and terms are approved before external testing.
- [ ] Temporary upload, report, and overlay retention/deletion policies are enforced and tested.
- [ ] Reports/overlays use private storage and short-lived authorized download links; no private media is public.
- [ ] Production secret rotation, backup, monitoring, audit logging, incident response, and deletion requests are operational.
- [ ] Mobile/EAS signing access and environment variables follow least privilege.
- [ ] Reassess the 10 moderate transitive Expo CLI/config advisories before release; the currently suggested forced fix would downgrade to an incompatible Expo SDK and was not applied.
- [ ] Real staging provider configuration and deployed smoke tests pass.
- [ ] Android `preview-staging` build and physical-device matrix pass.

No public release is authorized while any required item remains unchecked.
