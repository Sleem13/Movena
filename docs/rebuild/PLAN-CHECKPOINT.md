# Movena plan checkpoint — 2026-09-13

Resume from the earliest incomplete dependency, not from the number of screens
already built. A connected compatibility route is not transferred domain ownership.

| Original stage | Evidence and current state | Next acceptance gate |
|---|---|---|
| 1. Establish baseline | Initial inventory and representative synthetic workflows captured. Source SQLite backup/restore verified. | Finish deployed integration/permission inventory as domains move; keep initial inventory immutable. |
| 2. Build foundations | Flutter/Next clients, design tokens, localization, generated contracts and authenticated Django bridge exist. **Incomplete.** Identity import, sessions, recovery, guarded ownership transfer, projection, and delegated legacy reads now have local copy/restore and two-service evidence. | Rehearse on PostgreSQL with production-like service boundaries before activating. Expand modular domain ownership, contract coverage and deployment checks. |
| 3. Replace complete journeys | Accounts, connections, daily plans/check-ins, analysis/history, progress-report sharing, therapist review, scheduling and visit notes have connected clients and scoped tests. **Partial**, with legacy business writers. | Finish progress charts, commerce, goals/coaching, RehabRL, administration, notification preferences and remaining account/privacy workflows. Each journey needs native/web, API, design and acceptance evidence. |
| 4. Develop engine | Dataset validation, research pose/repetition primitives and candidate training entrypoint exist. **Research only.** | Implement task-complete engine/worker processing and separate decision-support training/evaluation. |
| 5. Validate/promote | **Blocked on evidence:** repetition baseline has zero evaluated videos. | Reviewed labels, participant-separated holdouts and task-complete rejection/quality/performance comparisons. No synthetic-test promotion. |
| 6. Cutover/cleanup | **Not started.** Original clients/backend/model entrypoints remain available. | Domain migration/restore and rollback, complete workflow parity, real-device upgrades, deployment monitoring and model promotion before removing the applicable legacy implementation. |

## Work resumed in this checkpoint

Return to stage 2's identity/data-preservation dependency. Added an isolated Django
identity module, an atomic read-only snapshot importer, legacy credential verifier,
and a compare-and-swap password upgrade hook that refuses legacy-owned credentials.
The hook is not wired to login, does not issue tokens and cannot transfer ownership.

Follow-on implementation adds durable opaque sessions, eligible-account login with
hash upgrading, account-wide revocation, single-use verification/password reset,
recovery issuance/cooldown and delivery-failure invalidation. A bounded legacy JWT
reader validates a configured signature algorithm/key and issuance cutoff, then
uses current identity state. Five HTTP endpoints have isolated contract tests;
they are intentionally not included in the live URL configuration. All 42 platform
and identity tests passed at that checkpoint.

Administrator status, role and password mutations and patient consent updates now
run in the isolated identity domain with current super-admin checks, protected and
legacy-owned account denial, conditional updates, session revocation and atomic
audit events. Public patient and administrator provisioning are implemented as
services. Public provisioning requires both accepted policies, exact configured
versions and HTTPS document URLs, returns a one-time verification delivery only to
the future email adapter, and stores only its digest. Patient creation/role changes
atomically queue an idempotent profile request containing only the account ID.
These additions brought the platform/identity suite to 53 passing tests.

The next bridge increment is now implemented behind disabled defaults. Platform
sessions can authenticate the v2 bridge only in explicit `transition` mode. Django
then issues a 20-second HS256 internal assertion bound to the account revocation
version, HTTP method, exact path and body digest. Legacy consumes each assertion
once using a durable nonce table and re-reads the projected account. Identity
mutation routes reject internal principals. A private, separately authenticated
projection endpoint stores no password material, uses a non-authenticating sentinel,
marks the row `identity_owner=platform`, protects it from legacy administration and
seeding, and creates the patient care profile idempotently. The platform/identity
suite now passes 78 tests; focused legacy identity/migration tests pass 11 tests.
Neither transition mode nor the shared secret is enabled in checked-in defaults.

Identity ownership transfer is now a guarded, dry-run-first operation. It verifies
the source snapshot and target rows exactly, requires an explicit long confirmation,
advances every account revocation version once, and queues one conversion intent per
account. The legacy conversion endpoint is separately disabled by default and uses
one-use signed assertions plus the expected legacy token version and password-hash
digest. A local two-service rehearsal converted all four copied accounts, removed
their legacy password material, authenticated a synthetic platform-owned patient,
and completed a delegated care read. Rollback was rehearsed before any platform
password upgrade. This evidence uses SQLite copies; production PostgreSQL and service
deployment acceptance remain outstanding.

The compatibility bridge also persists replacement-owned analysis lifecycle records
for observed submissions, polling and cancellation. It enforces local ownership,
preserves nullable values, distinct outcomes and engine/model versions, and exposes
an owner-scoped active-job list so web and native polling can resume after relaunch.
Processing still runs in the legacy engine until the replacement worker is complete.

An existing private source backup was imported into a new private Django database,
then backed up and restored into another new file. Four accounts and two consent
records match across all mapped fields, including permissions, protection/status,
recovery token hashes/expiry, revocation versions and original IDs. This is a local
SQLite rehearsal, not a live migration. Existing passwords were not requested or
tested; credential behavior was tested using synthetic known passwords.

## Immediate next work

1. Rehearse the tested identity writer transition on PostgreSQL with deployed service
   boundaries, real SMTP acceptance and public-edge throttling. Implement account
   downstream erasure completion. A dry-run-first startup backfill now reports and
   optionally creates only missing account-projection and patient-profile intents;
   it reports aggregate counts and cannot change credential ownership. Patient-owned export,
   correction and deletion requests now have durable, duplicate-safe records and
   protected administrator review. Approved deletion suspends the account, revokes
   sessions and records a configurable retention date without erasing clinical or
   commerce history. Registration, resend and reset
   requests now use a configurable Django email adapter; transition deployments
   fail closed unless SMTP, HTTPS frontend links and sender settings are configured.
   Real SMTP delivery and public-edge throttling still require deployment evidence.
   Protected root seeding is now an explicit environment-backed command: it cannot promote an
   existing ordinary or legacy-owned account, and an explicit reset revokes all
   sessions. Projection intent is now transactionally refreshed after provisioning, verification,
   revocation, recovery and administrator authority changes; a retrying Celery task
   and management command publish the latest state without clearing a concurrent
   replacement. Configure its deployment schedule before activation.
2. Rehearse the additive domain migration on PostgreSQL, then extend the persistent
   analysis lifecycle record into replacement worker ownership and restart recovery.
3. Continue remaining complete journeys while external model/device/policy gates
   are outstanding. Keep the status document specific about unverified behaviors.

Approved terms/privacy content, real-device and signing access, and model labels
remain separate gates. They do not prevent implementation of the next backend step.
