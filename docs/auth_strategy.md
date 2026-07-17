# Authentication Strategy

Local development uses email/password accounts, bcrypt hashes, short-lived JWT access tokens, and admin, therapist, patient, and researcher/demo roles. SQLAlchemy supports SQLite locally and PostgreSQL later. It lacks production recovery, MFA, refresh-token rotation, revocation, and verification.

An external provider—Supabase Auth, Firebase Auth, Auth0, or Clerk—may later supply mature mobile identity and operations. Selection is deferred pending deployment, privacy, portability, and cost review.

Sprint 13 chooses replaceable local JWT auth. Do not use real patient data in development. Production requires stronger identity, consent, secure storage, auditability, secrets management, and privacy/security review.
