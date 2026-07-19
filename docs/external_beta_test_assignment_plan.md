# External Beta Test Assignment Plan

> Invite-only beta only. No public release. No real patient data. No clinical use. No diagnosis or treatment claims. The beta is blocked until private staging, the Android build, physical-device QA, and active feedback/support links are ready.

## Boundary

Assignments are for a controlled invite-only beta only; there is no public release, patient onboarding, clinical use, diagnosis, or treatment evaluation. Use non-identifying test videos only. Assignment execution is blocked until private staging, Android build/install, physical-device QA, support/feedback links, complete consent, and GO approval exist.

Use `data/processed/beta/external_beta_test_assignments.csv`. It remains header-only while no tester is invited or consented.

Allowed task types: `valid_test_video`, `invalid_static_video`, `upload_retry`, `network_interruption`, `rejected_result_review`, `camera_guidance_review`, `session_history_review`, and `auth_token_review`. Required result cases: `success`, `rejected`, `upload_error`, `auth_error`, `network_error`, and `not_applicable`.

Each consented tester should receive:

- at least two of the five supported exercise IDs;
- at least one intentionally invalid/static or rejected-result review using safe test data;
- at least one retry or controlled network-interruption task where safe;
- optional auth/session history task only with an approved beta account;
- no request to create symptoms, exceed comfortable effort, or test emergency behavior.

Assignments must include generated IDs, expected input type, result case, status, and technical notes only. `completed` means the task was genuinely performed and recorded; planned or blocked assignments never count as exercises tested. Stop and escalate on privacy/safety concerns, cross-user access, misleading score/rejection, repeated crashes, or unsafe wording.
