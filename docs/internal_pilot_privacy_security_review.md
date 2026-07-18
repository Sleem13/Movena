# Internal Pilot Privacy and Security Review

Sprint 26 automated review confirms required source disclaimer wording, SecureStore usage, standardized private artifact 404 responses, and privacy-safe summary fields. It does not verify deployed secrets/CORS, installed-build visibility, real artifact authorization, or voluntary evidence handling; those checklist rows remain open.

Status: **not approved for execution**. Complete and sign this checklist for the exact build/backend pair.

- [ ] Test plan prohibits real patient data and identifiable patient videos.
- [ ] Any debugging media is explicitly and voluntarily shared through a restricted approved channel.
- [ ] Authentication, authorization, expiry, logout, and invalid-token behavior pass on staging.
- [x] Mobile source uses platform SecureStore for access tokens.
- [ ] Deployed staging `SECRET_KEY` is strong, non-default, provider-managed, and not exposed.
- [ ] Staging CORS contains only reviewed HTTPS frontend origins and no wildcard.
- [ ] Report/overlay links are signed, short-lived, authorization-tested, and not logged.
- [x] Artifact cleanup and retention behavior are documented.
- [x] Tester onboarding and known limitations prohibit clinical use and patient data.
- [ ] Safety copy is visible and verified on the exact installed build.
- [x] Feedback schemas avoid diagnosis/treatment fields and clinical claims.
- [x] Screenshots/videos are voluntary and recorded only as externally restricted evidence.
- [ ] Pilot owner, privacy owner, security owner, and safety reviewer approve the go/no-go record.

Stop affected testing for unauthorized access, token/secret exposure, identifiable data, public artifact access, diagnostic/treatment language, missing safety copy, or unexpected retention. Do not use pilot evidence as clinical validation.
