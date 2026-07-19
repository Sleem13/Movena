# External Beta Data Review and Cleanup

> Invite-only beta only. No public release. No real patient data. No clinical use. No diagnosis or treatment claims. The beta is blocked until private staging, the Android build, physical-device QA, and active feedback/support links are ready.

## Boundary

This review applies only to an invite-only, non-public product beta using non-identifying test data. It must not retain real patient data, health information, diagnosis, or treatment details. Execution is blocked until private staging, Android build, physical QA, support/privacy links, and retention operations are verified.

At each check-in and closeout:

1. Review roster, consent, assignments, feedback, and issues for unexpected identifiers or health narratives.
2. Move safety/privacy incidents to restricted handling; do not copy sensitive content.
3. Quarantine and delete inappropriate uploads/artifacts under the incident/deletion process.
4. Confirm completed assignments and exercises are based on actual records, not plans.
5. Record retained privacy-safe beta data, purpose, owner, access, and deletion date.
6. Process withdrawal/deletion requests through `[DELETION/PRIVACY CONTACT]`.
7. Run `python scripts/cleanup_artifacts.py --dry-run`, review the resolved artifact root and candidates, then run without `--dry-run` only under authorized operations.
8. Verify expiration/cleanup in staging storage, provider logs, and backups; local cleanup alone is insufficient.

Never delete raw project datasets or source training data through the artifact cleanup workflow. Current Sprint 29 local dry-run found 0 eligible artifacts and changed nothing; staging scheduling remains blocked.
