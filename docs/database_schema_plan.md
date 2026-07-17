# Database Schema Plan

PostgreSQL is the preferred future system of record. No database is connected in the current MVP.

## Identity and Profiles

| Table | Purpose | Key fields | Relationships | Privacy/security notes |
|---|---|---|---|---|
| `users` | Authentication subject and lifecycle | `id`, `external_auth_subject`, `role`, `status`, timestamps | Parent of one therapist or patient profile | Keep identity-provider secrets out of this table; restrict lookup and soft-delete lifecycle |
| `therapist_profiles` | Professional-facing profile | `user_id`, display name, organization, credential reference, verification status | One-to-one with `users`; linked to authorized programs | Credential text is not proof of licensure; verification data is restricted |
| `patient_profiles` | Minimal patient preferences and consent state | `user_id`, pseudonymous clinic reference, locale, accessibility preferences, consent version | One-to-one with `users`; parent of programs and sessions | Minimize demographics and separate identity from movement data |

Profiles use one-to-one foreign keys to `users`. Clinical credentials require a separate verification process; a text field is not proof of licensure.

## Catalog and Programs

| Table | Purpose | Key fields | Relationships | Privacy/security notes |
|---|---|---|---|---|
| `exercise_catalog` | Versioned active/planned exercise definitions | `id`, `exercise_key`, `status`, `analyzer_version`, instructions | Referenced by assignments and sessions | Only approved versions are active; instructions are versioned and sanitized |
| `exercise_programs` | Therapist-created plan container | `id`, `patient_id`, `therapist_id`, status and dates | Belongs to an authorized therapist-patient relationship; contains assignments | Row-level authorization and audit changes to plan ownership/status |
| `assigned_exercises` | Therapist-entered schedule and parameters | `id`, `program_id`, `exercise_id`, sets, reps, frequency, side, instructions | Child of program; references catalog | Treat instructions as sensitive care-plan text; never present them as AI prescriptions |

Programs belong to one patient and therapist relationship. Assignment values are human-entered care-plan data, not automated prescriptions.

## Analysis and Observations

| Table | Purpose | Key fields | Relationships | Privacy/security notes |
|---|---|---|---|---|
| `analysis_sessions` | Processing and session lifecycle | `id`, patient/assignment/exercise IDs, status, view, versions, validity/confidence | Belongs to patient; optional assignment; parent of metrics, issues, media, reports | Opaque IDs, tenant authorization, immutable processing provenance |
| `session_metrics` | Typed measurement values | `id`, `session_id`, metric key/value, unit, aggregation, confidence | Many-to-one with session | Allowlisted metric keys; suppress misleading comparisons when confidence is low |
| `detected_issues` | Versioned educational observations | `id`, `session_id`, issue key, rule version, evidence summary | Many-to-one with session | Use non-diagnostic vocabulary; restrict detailed evidence to authorized viewers |
| `uploaded_media` | Media lifecycle and consent | `id`, `session_id`, storage key, type, checksum, retention/deletion timestamps | Many-to-one with session; binary content in object storage | Encrypted storage, signed short-lived access, consent, malware/media validation, deletion propagation |
| `reports` | Generated report metadata | `id`, `session_id`, storage key, version, checksum, expiry | Many-to-one with session; references artifact object | Authorized short-lived access; reports retain disclaimer and versions |

Large frame arrays and raw landmarks should use encrypted object storage or an approved analytical store, not unbounded JSON rows in the transactional database.

## Governance

| Table | Purpose | Key fields | Relationships | Privacy/security notes |
|---|---|---|---|---|
| `model_versions` | Trusted model artifact registry | `id`, version, status, checksum, feature contract, evaluation reference | References one training dataset version; referenced by sessions/releases | Load only trusted checksummed artifacts; promotion and rollback are audited |
| `dataset_versions` | Reproducible data provenance | `id`, version, registry/mapping/split checksums, annotation and license status | Parent of annotations; referenced by models | Store provenance, consent/license summary, not raw participant media |
| `manual_annotations` | Versioned human review | `id`, dataset/sample references, pseudonymous participant/session, reps, labels, view, quality, annotator, confidence, adjudication | Belongs to dataset version/sample; may reference source reviews for adjudication | Annotator identity restricted; no direct identifiers; preserve disagreement history |

Production should also include append-only audit events, consent records, access grants, and deletion jobs even though they are not listed as core domain tables.

## Relationships

`users` link to therapist/patient profiles. A therapist and patient connect through an authorized care relationship before programs or session access. Programs contain assigned exercises. Sessions reference the catalog item and optional assignment. Metrics, observations, reports, and media belong to one session. Model and dataset versions are immutable references used by sessions and release records.

Manual annotations belong to an immutable dataset version and sample identity. Multiple reviewer rows may exist; an adjudicated record references its source reviews rather than overwriting disagreement history. Annotator identities are access-controlled and are not exposed in patient-facing analysis responses.

## Privacy and Security

- Collect the minimum necessary data; keep identity separate from movement measurements where possible.
- Use managed encryption in transit and at rest, field-level protection where justified, and encrypted object storage for media.
- Enforce row/tenant authorization in the application and test against insecure direct-object references.
- Use opaque IDs, short-lived signed artifact URLs, secret rotation, least privilege, audit logging, and deletion propagation.
- Define regional retention, backup, legal hold, export, correction, and account-deletion policies before persistence.
- Never place diagnoses or sensitive notes in logs, object keys, filenames, analytics events, or model features without an approved purpose.
# Sprint 11 Profile Extension

`patient_profiles` stores synthetic development profiles. `analysis_sessions.patient_id` is nullable and uses a logical `SET NULL` relationship; profile deletion explicitly unassigns sessions. A narrow SQLite compatibility migration adds the nullable column to existing local databases. Versioned Alembic migrations remain required before production deployment.
# Deployment note

SQLite remains appropriate only for local development. A hosted deployment should use managed PostgreSQL (for example Neon, Supabase, or Railway), migrations, encrypted backups, least-privilege credentials, and per-user authorization. The current schema must not be treated as a production clinical record.

Sprint 13 adds development users, optional versioned consent records, audit-log foundations, and nullable `owner_user_id` / `created_by_user_id` session ownership. The compatibility initializer adds missing SQLite ownership columns, but production requires versioned migrations and reviewed foreign-key/tenancy constraints.

## Sprint 14 research registry boundary

The Sprint 14 dataset, exercise-taxonomy, unified-sample, and model registries are versioned research and engineering metadata files. They do not create patient records, activate a runtime exercise analyzer, or authorize a model for production use. If these registries later move into persistent storage, their schema migrations, checksums, provenance, review status, and promotion history must remain separate from patient/session tables and be governed through an audited release process.
