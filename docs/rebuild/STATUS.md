# Movena rebuild status — 2026-09-14

**Partial implementation: connected recovery, accounts, plans, health profile, data rights, inbox, history, scheduling and visit-note clients; verified Android debug APK.**
This is not the complete replacement, a production release, or a cutover approval.
See [the plan checkpoint](PLAN-CHECKPOINT.md): work has returned to the incomplete
stage 2 identity/migration foundation before claiming further cutover progress.
Existing `frontend/`, `mobile/`, deployments and model entrypoints remain active.
The legacy backend remains authoritative; this stage adds two authorized visit-note
read endpoints, a shared read helper and an optional author-name response field. No retained capability has been cleared for removal.

## Implemented

| Area | Concrete implementation |
|---|---|
| Baseline | Static inventory of 130 routes, 32 models, 32 foreign keys, 27 native routes, 21 web pages and 7 locally present model artifacts with SHA-256 fingerprints. Routes record dependency guards, provisional domain ownership and removal gates. This is not a deployed-permission audit. |
| Design | Initial role concept board and recovery, scheduling, accounts, care-plan, health/inbox, history, data-rights and visit-note screen/component specifications. Shared light/dark tokens, English/Arabic catalog and exercise names; responsive web shell; native Material controls. Existing Movena launcher artwork is packaged in the Flutter projects. |
| Web | Next.js/TypeScript app with patient, therapist and administrator navigation; login/logout and recovery-request form; Today, response editing, symptom acknowledgement, analysis upload/playback/job lifecycle/result display, history, care connections/invitation responses, patient invitation and clinician review. Registration, verification and password-reset pages handle explicit consent and one-time links. Therapist care-plan authoring/revisions preserve history. Patient health editing, consent history, data-rights submission/history, inbox/read actions and symptom-flag editing are connected. Protected super administrators can review data-rights requests with explicit approve/reject reasons. History includes paging, explicit outcome filters and preserved zero/unavailable values. Therapists can create bounded progress reports and explicitly share them; patients can list and securely open shared reports. Scheduling adds booking, rescheduling, reason-based cancellation, staff status changes, weekly availability and short-lived video join links. Appointment note history and private-by-default clinician note creation are connected, including explicit patient sharing and frozen ambiguous retries. Unreplaced sections explicitly link to the existing product. |
| Native | Flutter Android/iOS source with secure token storage, session repository, care repository/check-in view model, analysis view model, camera adapter with audio disabled, gallery selection, video playback, patient Today/check-in/history/care and therapist patient review. Scheduling repository/view models connect booking, rescheduling, cancellation, status updates, weekly availability and external video joining. Patient Care/Account and administrator Operations/Account expose appointments. Arabic and theme preferences are shared. Registration, verification/reset custom links, plan authoring/revision, health editing, consent history, data-rights submission/history, inbox/read actions and editable symptom flags are connected. Protected super administrators can review data-rights requests. History paging and outcome filters retain access to older records. Therapists can generate and optionally share progress reports; patients can list and securely open shared reports. Appointment notes add author/date history, private-by-default creation, explicit sharing and frozen ambiguous retries. Other sections remain migration entrypoints. |
| API | Isolated Django REST `/api/v2` compatibility service. Every protected request revalidates legacy authentication; the legacy endpoint also enforces role/object permissions. Raw multipart forwarding, stable analysis submission receipts, safe outcome logging and a 38-operation generated OpenAPI core with 45 schemas. Data-rights submissions use retry receipts in compatibility mode; canonical review is super-admin-only, returns account identity only to that queue, and suspends approved deletion accounts. The transition identity service additionally records the retention deadline. Plan and visit-note submission receipts recheck current object access before replay and prevent ambiguous retries from creating duplicates. Visit-note reads enforce appointment ownership, active care access and explicit patient visibility. Progress reports enforce assigned-patient creation and patient sharing visibility; signed artifact links stay behind replacement client routes. An owner-scoped active-analysis endpoint lets web and native resume polling locally known jobs after relaunch. New account passwords enforce the legacy 72-byte bcrypt limit without changing existing login semantics. Scheduling requires stable booking keys, validates availability timezones and explicitly marks naive legacy appointment timestamps as UTC. |
| Persistence | Django receipts and the additive identity/session/consent/outbox models use a separate database. Read-only identity import verifies all fields atomically, preserves IDs/permissions/token versions and refuses changed targets. Raw legacy bcrypt verification, conditional upgrading, opaque sessions, recovery, provisioning, administrator mutations and policy-versioned consent are tested through isolated services/contracts. A guarded ownership-transfer command and separately gated legacy conversion endpoint advance revocation versions and remove legacy password material. Local copy-based transfer/rollback and two-service login/delegated-read rehearsals passed for four imported accounts and two consents. Observed analysis submissions, polling and cancellation now create Django-owned lifecycle records with local ownership, nullable outcomes and engine/model versions while legacy processing remains active. PostgreSQL acceptance remains outstanding. Legacy services remain the sole live writers for business domains other than staged identity and analysis lifecycle metadata. |
| Engine research | Reviewed-label and participant-split validation, CPU TCN/boosted-tree candidate training entrypoint and a promotion evidence validator that checks aggregate and per-task regressions. New research primitives validate coordinate spaces and visibility, measure angles, and count stable complete cycles without bridging tracking gaps. Training requires world-coordinate/backbone provenance and visible normalization anchors. These are research tools, not a newly validated analysis engine. |
| Build configuration | Locked npm, pub and platform Python dependencies; isolated platform Dockerfile; GitHub workflow for API, web and Flutter checks, Android debug compilation and iOS simulator compilation. Local Android debug build and package checks pass. Workflow and container builds have not been executed remotely. |

Android capture has no microphone permission in the compiled APK. Backup and
device-transfer rules include only locale/theme preferences; restored installs
need to log in again. Captured media and secure tokens are excluded. These
packaging checks do not substitute for OS permission and restore tests.

The compatibility label `legacy-v1` identifies the adapter lineage. It is not an
inferred historical task-model version. Unknown model versions remain null and
historical records are not rewritten. Rejected/error results do not display
successful scores, and unavailable measurements are not converted to zero.

## Verification performed

| Check | Observed result |
|---|---|
| Next `npm run build` | Production compilation and TypeScript passed on Next 16.3.5 |
| Web `npm test` | 17 tests passed: data-rights boundaries/retry keys, report period/query and signed-link routing, private note defaults/nullable payloads and retry classification, proxy origin/path and canonical deployment origin, history paging/outcome boundaries, local calendar arithmetic/time parsing, secure video grants, token/password boundaries, plan payloads, nullable health fields, safe inbox destinations and complete Arabic exercise names |
| Django `manage.py test platform_api` | 23 tests passed: retry-safe data-rights submission, note validation, revoked receipt replay and unresolved note submissions, history query/null preservation, public recovery with expired sessions, auth/revocation, object denial, multipart, replay, unresolved submission, routing, redirects, privacy of outcome logs, booking keys/conflicts, invalid availability, UTC normalization, Unicode password bounds and authorized plan receipt replay/conflicts |
| Identity import/password foundation | Seven focused tests within the current suite cover Unicode/bcrypt limits, malformed credentials, guarded hash upgrade, inactive/unverified accounts, concurrent reset protection, read-only repeat import, dry-run rollback, schema drift, orphan consent, atomic duplicate rejection and redacted evidence. |
| Identity sessions, writers and contracts | Total platform/identity suite now passes 79 tests. Coverage includes persistent opaque sessions, current-role/version validation, all-session logout, imported single-use recovery tokens, cooldown/delivery-failure handling, race/transaction rollback, bounded legacy JWT compatibility, current-authority administrator mutations, protected/legacy-owner denial, versioned consent, policy-gated patient registration, generic resend/reset delivery, protected-root seeding, data-rights requests and retention-aware deletion review, dry-run-first transition-intent backfill, redacted audit/outbox content, patient-profile requests, latest-state projection publication, controlled ownership transfer and durable analysis lifecycle capture. Deployment settings require SMTP and HTTPS links before enabling transition identity outside development. Focused legacy tests add projection collision/ownership, one-use ownership conversion, patient-profile creation, replay, path/body binding, disabled defaults and isolation from identity writers. Transition mode remains disabled; no production identity transfer, downstream erasure, real SMTP acceptance or native/web production session cutover was performed. |
| Engine `unittest discover -s engines/recovery/tests` | 20 dataset/promotion and pose-processing tests passed; separate disposable NumPy checks verified normalization and rejection of invisible anchors |
| Flutter `flutter analyze` | No issues found on Flutter 3.47.4 / Dart 3.13.3 |
| Flutter `flutter test` | 31 tests passed: data-rights payload/retry behavior, active analysis recovery after relaunch, safe replacement report URLs, frozen note payload/key retries, patient read-only repository and Arabic note editor with appointment context, history paging/retry/stale-response isolation and Arabic layout, account links before/after session restoration, returning from a signed-in account link to login, registration consent defaults, account retries, immutable plan submission retries, Arabic plan/health forms, nullable health saves, inbox read failure/retry, token revocation/origin, login/role shell, Arabic recovery/booking at 320×700 with 200% text scaling, preserved check-in responses with explicit symptom-flag corrections, clinician attestation, stable booking retries, stale availability responses, video grant validation and retained cancellation input after failure |
| Android debug APK | Built successfully for arm64-v8a, armeabi-v7a and x86_64. Package `ai.movena.mobile.development`, version 2.0.0 (1), min SDK 24 / target 36. APK Signature Scheme v2 verifies using an Android Debug certificate. Packaging guard passes: camera hardware optional, microphone permission absent, locale/theme-only backup resources included. This is not a signed production upgrade or a device test. |
| Legacy workflow/backup pytest | 3 tests passed using disposable records. Workflow subprocess checks booking replay without duplicate records, conflicts, denied relationships, rescheduling, staff confirmation, cancellation reasons/windows and private video grants. It also checks verification/reset expiry and consumption, reset revocation, role denial, plan-version history, health round trips, notification owner isolation, shared progress-report visibility and all 43 synthetic history records across three pages with denied private records. Visit-note workflows verify private/shared filtering, literal content, author labels, foreign appointment denial and revoked clinician reads/writes. Provider HTTP and report rendering are mocked; recording/screenshare remain disabled and therapist ownership is verified. |
| Browser, real routes on isolated in-memory database | Patient login → Today → completed check-in → persisted count; symptom response → therapist login → patient review → clinician-attested outcome → reviewed state |
| Browser layouts | Desktop at 1440×1000; Arabic dark account at 390×844 and 320×740. The 320-pixel layout had no horizontal overflow. These checks are not a full visual/accessibility audit of every screen. |
| Scheduling browser workflow | Real Next → Django → legacy fixture routes: patient Care → booking → saved/upcoming → reschedule → therapist Schedule → confirm → cancel → history. Arabic dark schedule/slot controls fit 320×740, 768×1024 and 1440×1000 without horizontal overflow. Calendar popup crashes the Codex in-app browser; day controls completed the workflow, but native browser date/time pickers still need external-browser verification. |
| Accounts, plans and health browser checks | Real Next → Django → legacy fixtures: clinician publishes a revised plan; old version is paused and retained; patient Today shows the revision. Arabic health text survives save/reload. Arabic registration has unchecked consent and accepts Arabic username characters; invalid verification tokens show localized feedback and stay out of the URL. Health layouts fit 320×740, 768×1024 and 1440×1000; plan editor and registration fit 320 pixels. Inbox empty state verified; read/failure/ownership behavior is covered by widget and real-route tests. |
| History browser workflow | Production-mode Next on its canonical localhost origin → Django → isolated legacy fixtures: patient login, all three pages of 43 records, end-of-history disabling, rejected-only filtering resets paging, and rejected detail has no success metrics. Arabic dark history fits 320×740, 768×1024 and 1440×1000 without horizontal overflow; console error log was empty. |
| Visit-note browser workflow | Production Next → Django → isolated legacy fixture: clinician reads private/shared notes, creates a private literal-text note and an explicitly shared Arabic note. Patient sees exactly the two shared notes, no private notes or editor. Final page shows visit time and participant. Arabic dark layouts fit 320×740, 768×1024 and 1440×1000 without horizontal overflow; Arabic light desktop also inspected. Console error log was empty. Native note form at 320×740 and 200% text passes widget checks, not device acceptance. |
| Local SQLite backup/restore | Read-only backup of `backend/movena_dev.db`, then restore into a second new private file; fingerprints/counts matched, integrity `ok`, zero foreign-key violations. See `evidence/sqlite-restore.json`. No domain migration was performed. |
| Identity snapshot migration/restore | Existing private source backup → new isolated Django SQLite database → second new restored database. Four accounts/two consents, all mapped fields equal, identical repeated import inserts zero, source bytes unchanged, integrity `ok`, zero foreign-key violations. See `evidence/identity-rehearsal.json`. No live ownership transfer or real-account password check. |
| Identity ownership transfer/rollback | Exact copied snapshot and target verification, dry-run, guarded execution, one-time token-version advancement, four queued conversion intents and pre-upgrade rollback passed for four accounts/two consents. See `evidence/identity-transfer-rehearsal.json`. |
| Two-service identity bridge | Actual local FastAPI and Django processes converted all four copied accounts, removed legacy password material, authenticated a synthetic platform-owned patient and completed a signed delegated care read. See `evidence/identity-bridge-rehearsal.json`. No production cutover or real password was used. |

The source database contained four accounts, three patient profiles and five
analysis sessions, along with other records. Copies are in the Git-ignored
`.rebuild-private/` directory. Reports contain counts, not record contents.
Production databases and external payment/email/video services were not touched.

## Required work before cutover

1. **Complete the application journeys.** Profile/identity settings beyond the patient health fields,
   approved policy content and consent changes, progress
   charts, live video integration verification, commerce, notification delivery/preferences, goals,
   live/recovery coaching, RehabRL decision support, and administration/model
   operations still need complete replacement screens and acceptance checks.
   The current navigation or a compatibility route does not provide feature parity.
   Accounts, plans, health and inbox clients also use the temporary adapter. Public
   registration has no configured approved terms/privacy documents; the existing beta
   drafts contain unresolved placeholders and are not a production policy.
   Scheduling clients are connected through the adapter; actual native/external-browser
   date/time pickers, installation upgrades and real video visits are not verified.
   Visit-note history currently loads all notes for an appointment; large-history
   performance and cross-launch draft/submission recovery remain unverified.
2. **Transfer remaining domain ownership to Django.** Implement domain models/services,
   object-level authorization independent of legacy handlers, additive migration,
   activate the tested identity transfer only after the production rehearsal, integration adapters, migration
   count/relationship/credential checks, and domain rollback. Identity currently
   delegates to the existing verifier; no live hashes have been changed. Staged
   identity models/import and copy-based SQLite rehearsal plus isolated session,
   recovery, provisioning, administrator and consent services now exist. Email
   downstream erasure completion, projection task
   scheduling and PostgreSQL migration/rollback still need implementation and
   acceptance. Real SMTP delivery, bounce handling and public-edge rate limiting
   also need deployment evidence. The signed cross-stack reader, ownership conversion and latest-state publisher are
   implemented and passed a local two-service SQLite rehearsal, but remain disabled and unverified on PostgreSQL.
3. **Finish durable analysis orchestration.** Celery/Redis settings and Django-owned
   lifecycle records exist, but replacement workers and PostgreSQL processing ownership are not implemented. Current
   jobs run in the legacy engine. A receipt prevents duplicate submission after
   an uncertain outcome, but can remain unresolved without upstream
   reconciliation. Plan and visit-note receipts have the same unresolved-outcome limitation. Cross-launch recovery, interrupted uploads, worker restarts,
   Terminal reconciliation for jobs not subsequently polled, interrupted uploads, worker restarts,
   artifact expiry and lifecycle races require further work. Uploads are buffered
   through the preview proxy and need deployment load/size validation.
4. **Build and evaluate the new engine.** Research pose/repetition primitives now
   exist, but task-specific processing, validity/feedback integration and separate
   decision-support training/evaluation are unfinished.
   No training run or model promotion was performed. Existing benchmark evidence
   has zero evaluated repetition videos; reviewed labels, task-complete holdouts
   and paired performance/rejection results are mandatory. Do not promote from
   synthetic tests or validation-set metrics.
5. **Verify native and deployment behavior.** An isolated Android SDK 35/36,
   Temurin JDK 17, CMake 3.22.1, NDK 28.2 and checksum-pinned Gradle 9.3.1 are now installed. Android debug
   APK compilation and packaging checks passed; see `evidence/android-debug.json`. This machine still lacks macOS/Xcode and attached
   Android/iOS devices; no IPA or installation upgrade has been tested.
   Verify the existing Android certificate and higher build number, Apple team,
   `movena` deep links, camera/gallery permissions, playback, background/resume,
   keyboard, phone/tablet layouts and real-device accessibility. All-screen Arabic
   content, chart RTL, localized platform prompts, dark mode and screen-reader
   review remain incomplete. Docker is also unavailable locally.
6. **Rehearse production cutover and cleanup.** Complete contracts for retained
   operations, integration tests, monitoring/alerts, production-copy migrations,
   rollback and acceptance. Only then remove each superseded screen, dependency,
   route, deployment and training entrypoint. Retain migration/evaluation evidence.

Missing model evidence and device/signing access block their respective gates;
they do not prevent the remaining application/backend implementation work.

## Local development

The new stack is opt-in; it does not replace the existing development commands.

1. Install `services/platform/requirements.lock` into a separate Python 3.12
   environment, then run `python services/platform/manage.py migrate` against the
   new platform database. Never point it at the legacy database.
2. Set `MOVENA_LEGACY_API_URL` to the existing API origin and run
   `python -m uvicorn movena.asgi:application --host 127.0.0.1 --port 8020 --no-access-log`
   from `services/platform`. Environment examples document the settings; Django
   does not automatically load `.env` files.
3. From `apps/web`, run `npm ci` and `npm run dev`; use port 3100. Configure
   `MOVENA_PLATFORM_URL` and `MOVENA_WEB_ORIGIN` in `.env.local`. The latter must
   be the exact public browser origin (HTTPS in deployment), because Next may
   report an internal origin behind a proxy. Missing/invalid origins cannot
   authorize mutations. Local production verification used `http://localhost:3100`;
   configured-origin behavior is covered by unit tests, not a deployed proxy test.
4. Follow `apps/native/BUILDING.md` for Flutter configuration. Release builds need
   a configured HTTPS API and the original signing identities.

For disposable browser QA, `scripts/rebuild_fixture_server.py` starts selected
real legacy routes on loopback port 8040 with an in-memory database. Point the
new API at that origin. Its explicit synthetic fixture credentials are contained
in that script. It does not provide analysis workers or all legacy domains.

The checked-in baseline is the initial inventory; generate subsequent snapshots separately with `scripts/rebuild_inventory.py`; regenerate shared
contracts with `scripts/generate_rebuild_contracts.py` using the existing backend
Python environment, then run `dart format lib/generated` in `apps/native`.

