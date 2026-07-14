# Database Schema Plan

PostgreSQL is the preferred future system of record. No database is connected in the current MVP.

## Identity and Profiles

| Table | Purpose | Main columns |
|---|---|---|
| `users` | Authentication subject and lifecycle | `id`, `external_auth_subject`, `role`, `email_hash` where needed, `status`, `created_at`, `deleted_at` |
| `therapist_profiles` | Professional-facing profile | `user_id`, display name, organization, credential metadata/reference, verification status |
| `patient_profiles` | Minimal patient preferences and consent state | `user_id`, pseudonymous clinic reference, locale, accessibility preferences, consent version |

Profiles use one-to-one foreign keys to `users`. Clinical credentials require a separate verification process; a text field is not proof of licensure.

## Catalog and Programs

| Table | Purpose | Main columns |
|---|---|---|
| `exercise_catalog` | Versioned active/planned exercise definitions | `id`, `exercise_key`, `display_name`, `status`, `analyzer_version`, `instructions_json` |
| `exercise_programs` | Therapist-created plan container | `id`, `patient_id`, `therapist_id`, `status`, `start_date`, `end_date`, `notes` |
| `assigned_exercises` | Therapist-entered schedule and parameters | `id`, `program_id`, `exercise_id`, sets, reps, frequency, side, instructions, sort order |

Programs belong to one patient and therapist relationship. Assignment values are human-entered care-plan data, not automated prescriptions.

## Analysis and Observations

| Table | Purpose | Main columns |
|---|---|---|
| `analysis_sessions` | Processing and session lifecycle | `id`, `patient_id`, `assigned_exercise_id`, `exercise_id`, `status`, timestamps, capture view, analyzer/pose/model versions, validity/confidence summary |
| `session_metrics` | Typed or namespaced measurement values | `id`, `session_id`, `metric_key`, numeric/text value, unit, aggregation, confidence |
| `detected_issues` | Versioned educational observations | `id`, `session_id`, `issue_key`, severity band if approved, rule version, evidence summary |
| `reports` | Generated report metadata | `id`, `session_id`, storage key, version, checksum, expires/retained timestamps |
| `uploaded_media` | Media lifecycle and consent | `id`, `session_id`, storage key, media type, size, checksum, retention choice, expires/deleted timestamps |

Large frame arrays and raw landmarks should use encrypted object storage or an approved analytical store, not unbounded JSON rows in the transactional database.

## Governance

| Table | Purpose | Main columns |
|---|---|---|
| `model_versions` | Trusted model artifact registry | `id`, version, status, artifact checksum, feature contract, dataset version, evaluation reference, promoted/retired timestamps |
| `dataset_versions` | Reproducible data provenance | `id`, version, registry checksum, mapping version, split version, annotation status, consent/license summary |

Production should also include append-only audit events, consent records, access grants, and deletion jobs even though they are not listed as core domain tables.

## Relationships

`users` link to therapist/patient profiles. A therapist and patient connect through an authorized care relationship before programs or session access. Programs contain assigned exercises. Sessions reference the catalog item and optional assignment. Metrics, observations, reports, and media belong to one session. Model and dataset versions are immutable references used by sessions and release records.

## Privacy and Security

- Collect the minimum necessary data; keep identity separate from movement measurements where possible.
- Use managed encryption in transit and at rest, field-level protection where justified, and encrypted object storage for media.
- Enforce row/tenant authorization in the application and test against insecure direct-object references.
- Use opaque IDs, short-lived signed artifact URLs, secret rotation, least privilege, audit logging, and deletion propagation.
- Define regional retention, backup, legal hold, export, correction, and account-deletion policies before persistence.
- Never place diagnoses or sensitive notes in logs, object keys, filenames, analytics events, or model features without an approved purpose.
