# Identity migration foundation

The `identity` Django app stores staged accounts and consent rows. Live `/api/v2`
authentication still delegates to `/api/v1`; nothing reads staged accounts to grant
API access. No migration changes the legacy database or its active password hashes.

`Account.user_id` retains the original external ID; `legacy_id` retains the original
numeric ID. All account fields and consent IDs are mapped explicitly. Permission
JSON, role, status/protection flags, revocation version, nullable values and recovery
token hashes remain unchanged. Naive legacy timestamps are interpreted as UTC.
Unrecognized schema changes, invalid values, orphan consents, duplicate identities
or target conflicts abort the whole import. An identical repeat is a no-op; this
is not a live incremental-sync mechanism.

`import_identity_snapshot` reads SQLite in read-only mode and verifies every mapped
target field. Its default is a transaction rollback; `--persist` stages rows in the
configured target. Never use the legacy database as Django's migration target.
Imports always leave `credential_owner=legacy`. Ownership changes only through the
separate guarded transfer procedure documented below. Source copies and target databases contain credentials
and personal records and belong in the Git-ignored private rehearsal directory.

The verifier supports legacy raw UTF-8 bcrypt and Django hashes without rewriting
credentials. It rejects malformed bcrypt hashes and passwords beyond bcrypt's
72-byte boundary, matching this repository's installed bcrypt 5 behavior. The
separate upgrade hook requires platform ownership, an eligible account and a valid
password. A conditional update checks the previous hash and revocation version so
a concurrent reset wins. It uses Django's configured password hasher; it does not
issue sessions or change permissions. See [Django password management](https://docs.djangoproject.com/en/5.2/topics/auth/passwords/)
and [bcrypt documentation](https://pypi.org/project/bcrypt/).

## Rehearsal

Run with the replacement Python environment. Both destination paths must be new;
the command refuses existing files. Use a stable, previously verified source copy.

```powershell
.venv-rebuild/Scripts/python.exe scripts/rebuild_identity_rehearsal.py `
  .rebuild-private/movena-copy-20260912.sqlite3 `
  .rebuild-private/identity-new.sqlite3 `
  .rebuild-private/identity-restored-new.sqlite3 `
  --output docs/rebuild/evidence/identity-rehearsal.json
```

The script exclusively creates the targets, applies additive Django migrations to
the isolated target, imports and checks an identical repeat, restores a backup and
compares every mapped field again. Evidence contains counts/booleans only. No user
password is requested, printed or tested. Synthetic-password tests cover Unicode,
wrong passwords, malformed hashes, ownership gating and concurrent resets.

Verified locally: four accounts, two consents, unchanged source bytes, exact mapped
fields, no duplicate rows on repeat, restored integrity `ok` and zero foreign-key
violations. See `evidence/identity-rehearsal.json`.

Before activating identity ownership: connect the tested login/session, recovery,
provisioning, administrator mutation and consent core to both stacks; finish
deletion/retention and downstream identity projection scheduling; verify real SMTP
delivery and public-edge throttling;
all object permissions; quiesced final import or reviewed delta capture; PostgreSQL
verification; and rollback after a password has been upgraded. Restoring a stale
password database alone is not an acceptable rollback of live credential changes.

## Session and recovery core

`identity.sessions` now issues opaque `mv2_` sessions and stores only their SHA-256
digests, expiry and observed account revocation version. Authentication re-reads
current account eligibility/ownership/version. Logout and successful password
recovery increment that version; all old sessions then fail. Login upgrades raw
bcrypt only for platform-owned eligible accounts and conditionally updates the
observed credential so a concurrent reset cannot be overwritten.

Imported verification/reset links use the same token digests as the legacy writer.
Consumption clears the token atomically with the identity update and audit event.
Recovery issuance applies a conditional cooldown, exposes plaintext only to the
future delivery adapter, and returns no result for missing/ineligible accounts.
Delivery failure clears only its matching token, retains cooldown and cannot erase
a newer request. Delivery transport/outbox and public request throttling still need
integration before exposing these operations live.

`identity.legacy_sessions` verifies existing HMAC JWTs with an explicitly supplied
server key/algorithm, final issuer timestamp and finite acceptance deadline. It
rejects expired/newly issued/malformed tokens and uses the current stored role,
permissions and revocation version rather than trusting old role claims. No live
key is loaded; asymmetric issuer migration is not implemented. The PyJWT dependency
is pinned; algorithm handling follows its [API reference](https://pyjwt.readthedocs.io/en/stable/api.html).

`identity.urls` exposes login/me/logout/verify-email/reset-password through the live
URL configuration only when `MOVENA_IDENTITY_MODE=transition`. The default remains
`legacy`, so `movena.urls` continues routing live requests to the legacy bridge.
Tests verify both old and new token revocation through the
same HTTP interface, stale bearer recovery, no upstream fallback and no credential
fields in account responses. These are synthetic integration tests, not production
cutover or real-client acceptance of Django-owned sessions.

The writer inventory includes `auth.py`, `admin.py`, patient consent writes,
`admin_seed_service.py`, and `db/database.py` permission backfills. Registration
and role changes also create care profiles; legacy care/notification queries read
User records directly. All require a reviewed owner/reader transition before
activating the new identity API. Flipping one login route alone is insufficient.

## Provisioning, administration and consent

The isolated identity domain now implements public patient and administrator account
provisioning. Public creation requires explicit acceptance of configured terms and
privacy versions with HTTPS document URLs; privileged roles require a current
platform-owned super administrator. New accounts use UUIDs and leave `legacy_id`
null, while imported records retain their original numeric ID. Public accounts are
unverified and receive a single verification secret for the future delivery adapter;
only its digest and expiry are persisted. No registration route is live and no
policy document is configured or accepted on a user's behalf.

Status, role and administrator password changes reject protected super-admin and
legacy-owned targets. Changes use observed-state conditional updates and increment
the revocation version when authority or credentials change. Audit events retain
actor, reason and safe transition metadata; password values never enter audit or
outbox records. Consent updates accept only a configured policy version. Imported
consent IDs remain unchanged; new consent records use Django's local sequence and
carry the policy URL.

Patient creation and transition to the patient role enqueue one transactional
`patient_profile.requested` outbox record. The event payload contains only `user_id`
and has a unique aggregate/event constraint, so retries do not request duplicate
profiles. Account provisioning, verification, revocation, recovery and administrator
authority changes also refresh one `account.projection_requested` latest-state
intent. Its payload contains only the account ID and revision.

## Transitional legacy reader

The legacy backend has an additive `identity_owner` account field and durable
`internal_principal_nonces` table in Alembic revision `0010_identity_projection`.
Its private account projection endpoint accepts only a 20-second HS256 assertion
whose issuer, audience, subject, method, exact path and body digest validate. The
nonce is committed once; replay fails across workers. The projection contains
current account/profile authority fields and permissions, never password or
recovery material. Its legacy password column receives `!platform-owned`, which
cannot authenticate. Legacy user mutation and seed paths reject these rows.

For a platform session, transition-mode Django signs the specific legacy care
request with the account's current revocation version. Legacy checks the signature,
one-use nonce, projected ownership, current active state and matching version before
its existing role/object authorization runs. Internal principals are forbidden from
legacy identity mutation and user-administration routes. Request bodies are hashed
only for this private scheme, so public video uploads are not newly buffered.

Both services leave this facility disabled when
`MOVENA_INTERNAL_ASSERTION_SECRET` is empty. Django refuses transition mode unless
the shared secret has at least 32 characters. `project_platform_accounts` provides
an explicit idempotent bootstrap projection command and the private endpoint creates
a missing patient care profile. `publish_identity_projections` is available as both
a retrying Celery task and a bounded management command. It marks only the exact
intent it sent, so an identity change during the network call remains pending.
Deployment scheduling and a PostgreSQL rehearsal remain required before activation.

## Controlled ownership transfer

`transfer_identity_ownership` is the only operation that changes imported account
ownership. It opens the named SQLite source read-only, verifies integrity and foreign
keys, requires the exact target account/consent set and field values, and defaults to
a rolled-back dry run. Execution is available only while identity mode remains
`legacy`, only if the source fingerprint has not changed, and only when the value of
`MOVENA_IDENTITY_TRANSFER_CONFIRMATION` is at least 32 characters and exactly matches
the command confirmation. The confirmation is read from the environment rather than
the command line.

Execution atomically marks each imported account platform-owned, advances its token
version exactly once, and queues `account.ownership_transfer_requested`. The legacy
private conversion endpoint is independently gated by
`MOVENA_ALLOW_IDENTITY_OWNERSHIP_TRANSFER`; it accepts a one-use signed
`identity-transfer` assertion and converts only when both the old token version and
SHA-256 digest of the old password hash match. It then replaces the legacy password
with the non-authenticating `!platform-owned` sentinel. The ordinary projection
endpoint continues to reject legacy-owned collisions.

Use this order for a deployment rehearsal or cutover:

1. Quiesce legacy identity writers and take the final verified source snapshot.
2. Import that exact snapshot into the isolated platform database.
3. Run `transfer_identity_ownership <snapshot>` without `--execute` and review it.
4. Configure the shared assertion secret and briefly enable the legacy conversion endpoint.
5. Set the confirmation environment value and run the command with `--execute` while identity mode is still `legacy`.
6. Publish ownership-transfer intents until none remain, then verify projected counts, relationships, sentinel passwords and revocation versions.
7. Disable the conversion endpoint and remove the transfer confirmation value.
8. Run the normal projection backfill/publisher, enable transition mode, and verify login plus delegated care reads.

Rollback to legacy ownership is valid only before any platform password upgrade or
other platform-owned identity write. Once such a write occurs, restoring a stale
legacy credential store can restore revoked credentials and is prohibited.

The local evidence in `evidence/identity-transfer-rehearsal.json` verifies dry-run,
execution and pre-upgrade rollback for four copied accounts and two consents. The
two-service evidence in `evidence/identity-bridge-rehearsal.json` verifies conversion
of all copied accounts, sentinel legacy passwords, synthetic platform login and a
signed delegated care read. Neither rehearsal touched production or tested a real
account password; PostgreSQL and deployment acceptance remain outstanding.

## Protected root provisioning

`seed_protected_superadmin` is the only identity service path that creates a
`super_admin`. Public and ordinary administrator provisioning reject that role.
The command reads four `MOVENA_SUPER_ADMIN_*` environment values and never accepts a
password argument that would appear in shell history. Repeated execution leaves an
already protected platform root unchanged. `--reset` works only for that same
protected account, increments its revocation version, invalidates existing sessions,
records a redacted audit event and refreshes its projection intent. It refuses to
promote an ordinary, unprotected or legacy-owned account.

## Registration and recovery delivery

Transition routing now owns registration, verification resend and password-reset
requests. Registration remains unavailable until exact approved terms and privacy
versions with HTTPS URLs are configured. Public creation is patient-only and returns
the safe account profile; verification and reset secrets are sent through Django's
email backend and never returned by HTTP or stored in plaintext. A failed registration
delivery clears only its matching verification secret so a later resend can recover.

Recovery-request responses are identical for absent, ineligible, throttled and
temporarily undeliverable accounts. Issuance retains the existing cooldown and
single-use digest behavior. Development may use the console backend. Outside
development, transition mode requires SMTP, an HTTPS frontend origin, a configured
host and valid sender address. Local tests use the in-memory backend; actual provider
delivery, bounce handling and edge rate limits remain deployment gates.

## Data rights and retention

Transition mode owns patient data-rights history and submission plus the protected
administrator review queue. Export, correction and deletion requests are durable;
repeating an open request returns the existing record. Review decisions require a
current platform-owned protected root and a recorded reason.

Approving deletion suspends the account, increments its revocation version, invalidates
sessions, refreshes the legacy projection and records `retention_until` using the
configured delay. It does not delete or anonymize identity, care, analysis, commerce
or notification records. Completion remains unavailable until those domain owners
report their retention decisions and a rehearsed erasure workflow proves required
history is preserved.

`backfill_transition_intents` audits every platform-owned account and patient. Its
default is report-only; `--persist` creates only missing account-projection and
patient-profile intents. Repeated application is a no-op, legacy-owned accounts are
excluded, and the command cannot transfer credential ownership.
