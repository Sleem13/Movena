# Care connections rollout

## Behavior

Accounts retain a single role. A patient can be independent or connected to multiple
therapists. Existing active assignments remain active, with source `legacy`; no
historical consent is invented. Newly accepted invitations use `invitation`, and
direct administrator assignments use `admin`.

Therapists manage invitations and connections from Caseload > Care connections.
Patients use My care team. Administrators use More tools > Patient assignments.
Independent patients retain their existing self-directed features.

Invitations expire after seven days, require the invited verified patient account,
and use hashed, single-use tokens. Resending rotates the token. SMTP failures leave
a saved invitation with failed delivery status; the therapist can resend it.
Existing verified patients can also respond directly in My care team. Invitation
links use a URL fragment, retained in session storage through registration/login;
it is removed after response or dismissal. No raw token is returned by the API.

Invitations targeting an existing profile never silently merge another patient
account. Conflicting legacy profiles require an administrator-reviewed data-linking
procedure; automatic account linking and record merging are not provided.

Ending a connection retains patient records and plans but removes therapist access
to linked clinical APIs, queued job results, report/media downloads and future
clinical email delivery. Creator identity and old signed artifact URLs do not bypass
the relationship check. Downloads already obtained cannot be recalled. Meeting
tokens already issued by a video provider remain subject to that provider's expiry;
ending a relationship does not remotely erase downloaded records or live sessions.

Unassigned legacy profiles are administrator-only until explicitly assigned.
Therapists cannot delete account-linked patient profiles or patient-linked sessions.
New plans replace only that author's active plans; plans from other therapists remain
visible in the patient's daily care. Plan status changes require the author or admin.

## API changes

- `GET /api/v1/connections`: actor-scoped active/ended connections and display names.
- `POST /api/v1/connections/{id}/end`: participant or administrator; admin reason required.
- `GET/POST /api/v1/care-invitations`: own invitation inbox or therapist invitations.
- `POST /api/v1/care-invitations/lookup`: authenticated invited patient; token in body.
- `POST /api/v1/care-invitations/{id}/respond`: accept/decline; optional link token.
- `POST /api/v1/care-invitations/{id}/resend` and `/cancel`: originating therapist only.
- Existing `POST /api/v1/admin/assignments` now requires a nonblank `reason`; existing
  response fields are retained. Update external clients before rollout.
- `GET /api/v1/admin/assignment-options`: patient search and unassigned filter,
  active therapist options. Patient options are limited to 100 matches; refine search.
- Patient-linked analysis requires `save_session=true` for durable access control.

## Deployment

1. Back up the staging database and validate that the backup can be restored. Record
   the current Alembic revision and counts of users, patients, assignments, plans,
   sessions and reports. Do not rename identifiers or move existing patient data.
2. Review legacy profiles without active assignments. Do not infer assignments from
   names, email addresses or the last clinician who viewed a record.
3. Confirm `FRONTEND_URL` points to the intended frontend and SMTP is configured.
   Console email delivery is for local verification only.
4. Pause application writers during the schema upgrade. From the repository root,
   using the target environment's database URL, run `alembic upgrade head`.
   Expected head: `0008_care_connections`. The migration is additive and handles
   both existing databases and baseline metadata-created tables.
5. Deploy/restart the backend and frontend together. Verify counts and assignments
   match the backup and legacy sources are marked accurately. Production startup
   rejects an older schema. No automatic downgrade deletes connection history.
6. Run the staging smoke test below with synthetic accounts, not real patient data.
   Watch invitation delivery failures, authorization denials and connection audit
   events. Ended connections with upcoming appointments produce administrator
   notifications and `connection.appointments_need_review` audit events; review
   and cancel/reschedule those appointments using the existing scheduling workflow.

For rollback, retain the additive schema and restore reviewed application versions
only after checking their schema-version guard. Do not drop invitation or clinical
tables. Use a reviewed forward fix or a verified backup restoration process.

## Verification

Use separate admin, therapist, second therapist, patient and unrelated patient
accounts. Assign directly with a reason; verify both parties see the connection.
End it as the patient, then invite by email and accept after login/verification.
Connect a second therapist, ensure both clinicians see the record, and disconnect
only one. Verify that clinician cannot retrieve sessions, PDF reports, media or
queued job results, including with old signed links. Confirm patient records and
the second therapist's access remain intact. Check resend invalidates the old link,
decline/cancel/expiry deny activation, and unrelated accounts cannot respond.

Local automated coverage includes SQLite fresh/existing migrations, concurrent
activation, lifecycle and access tests, notification suppression, multiple-author
plans, UI actions and the frontend build. Browser checks use an isolated synthetic
API/database and cover desktop, 320/390px mobile, Arabic/RTL, consent-dialog focus
and the invitation login handoff. Live PostgreSQL, SMTP and provider video-token
revocation need deployment-environment verification; no production changes are made
by these tests.
