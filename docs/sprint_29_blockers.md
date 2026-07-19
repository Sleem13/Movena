# Sprint 29 Execution Blockers

## Current decision

Sprint 28 ended **NO-GO**. Sprint 29 execution assets are being completed, but the invite-only external beta has not started. There is no public release, patient onboarding, real patient data, clinical use, diagnosis/treatment claim, or promoted ML/DL feature.

| Blocker | Current evidence | Required closure |
|---|---|---|
| Private staging | No deployed private HTTPS backend/web smoke record | Deploy reviewed staging; verify health/ready/auth/CORS/analysis/artifacts/retention |
| Android build | `0.28.0-rc.1` registry says `blocked_not_submitted` | Configure real EAS preview URL, build private APK, record/install artifact |
| Physical-device QA | No approved Android launch/upload/network/token/artifact matrix | Execute and sign final QA on supported devices |
| Feedback/support links | Install/login/feedback/issue/support/privacy/deletion/status placeholders inactive | Assign owners, activate private links, test access/escalation/revocation |
| Tester roster | Header only; 0 real tester records and 0 invitations | Add aliases only after GO and authorized selection |
| Consent | Header only; 0 acknowledgement records | Record versioned affirmative consent before assignments/uploads |
| Assignments | Header only; 0 assignment records | Assign only consented testers after GO |
| Beta results | 0 feedback and 0 issue rows; monitoring says `not_started` | Collect genuine product-QA evidence after safe execution begins |

## Infrastructure gate check — 2026-07-19

- Render, Neon, and Vercel credentials/project configuration are unavailable locally; no HTTPS staging deployment or PostgreSQL instance could be created.
- EAS authentication succeeds, but the `preview` environment has no variables, including no `EXPO_PUBLIC_API_BASE_URL`; the Android build was not submitted.
- No APK/install link or named physical Android device is available, so every physical-device scenario remains pending.
- Feedback, issue, support, privacy/deletion, consent, limitations, status, install, and login placeholders remain inactive.
- Automated suites may validate repository behavior but do not close deployed, device, link, legal/privacy, staffing, or accountable approval gates.

Empty logs are not proof of reliability, safety, usability, or clinical validity. The only permissible Sprint 29 final status is **execution-assets complete / beta blocked** until these gates close.
