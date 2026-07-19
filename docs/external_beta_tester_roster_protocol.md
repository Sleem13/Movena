# External Beta Tester Roster Protocol

> Invite-only beta only. No public release. No real patient data. No clinical use. No diagnosis or treatment claims. The beta is blocked until private staging, the Android build, physical-device QA, and active feedback/support links are ready.

## Boundary

The roster supports a future invite-only beta only, not a public release. Use aliases and test videos only; never record real patient data or health information. Participation is product QA, not clinical use, diagnosis, or treatment. No roster entry authorizes testing while staging, Android build, physical-device QA, feedback/support links, and release approval remain blocked.

The canonical file is `data/processed/beta/external_beta_tester_roster.csv`. It is intentionally header-only until a tester is genuinely selected and invitation is authorized.

## Data minimization

- Use generated `tester_id` and non-identifying alias; do not store names, email, phone, employer, diagnosis, symptoms, patient relationship, or exact location.
- Keep invitation contact details in the approved access-controlled invitation system, not this CSV.
- Record only platform/device/OS/build/environment data needed for QA.
- `assigned_exercises` contains exercise IDs, never health context.
- `notes` must contain technical logistics only.

Allowed `invite_status`: `not_invited`, `invited`, `accepted`, `declined`, `removed`. Allowed `testing_status`: `not_started`, `in_progress`, `completed`, `blocked`, `withdrawn`.

Only the beta program owner may add an authorized alias. A tester cannot move to `in_progress` without a matching complete consent record and approved assignments. Withdrawal/removal triggers access revocation, assignment stop, eligible-data deletion review, and a roster update without erasing the audit state. Restrict roster access to authorized beta operations and privacy/security reviewers.
