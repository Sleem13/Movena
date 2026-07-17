# Deployment Privacy Notes

## Development and demo boundary

Development and demo environments must not store real patient-identifiable data. Use synthetic or non-identifiable evaluation records and temporary videos. Local SQLite, local artifact directories, placeholder therapist profiles, and unauthenticated session APIs are not production patient systems.

## Production prerequisites

Before any real patient data is processed, a deployment requires:

- authenticated user identity and role-based patient, therapist, and administrator access;
- an explicit, reviewable consent workflow and withdrawal behavior;
- a secure managed database with encrypted transport/storage, migrations, backup, and deletion controls;
- private object/media storage with short-lived authorized access, retention, deletion, and auditability;
- secrets management, HTTPS, production CORS, monitoring, incident response, and privacy/security review;
- a documented data inventory, purpose limitation, regional legal assessment, and least-privilege access.

## Safety positioning

AI feedback supports exercise monitoring and education only. It does not diagnose, prescribe treatment, determine fitness for activity, or replace assessment by a licensed physiotherapist or healthcare professional. Low-confidence results require manual review. Product, model, security, privacy, and clinical research approvals are separate decisions.
