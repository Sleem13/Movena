# Development Profile Data Policy

`PatientProfile` is a prototype grouping mechanism, not a patient record. Use synthetic UUIDs and placeholder display names only.

Allowed development fields are display name, broad age group, broad sex category, broad clinical-group placeholder, and non-sensitive notes. Do not store names, dates of birth, addresses, contact details, medical-record numbers, diagnoses, treatment plans, or other identifiable/sensitive health information.

Deleting a profile unassigns its sessions and deletes profile metadata; it does not delete session metadata or artifacts. Production profile handling requires a reviewed legal basis, consent, minimization, access controls, encryption, auditability, retention/deletion policy, and incident response.
