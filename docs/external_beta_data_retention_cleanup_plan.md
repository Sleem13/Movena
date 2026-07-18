# External Beta Data Retention and Cleanup Plan

## Allowed data and duration

- Uploaded test video: temporary processing only; remove after request completion/failure.
- Generated overlay/report artifacts: configured maximum 24 hours for this candidate, then cleanup.
- Session metadata saved by an authenticated tester: retain only for the approved beta evaluation/closeout window; final duration must be approved before GO.
- Feedback, issue, build, and QA records: privacy-safe aliases/technical metadata only, retained through beta closeout and the approved audit window.
- Security/provider logs: minimum fields and shortest approved operational period; no media, source filenames, raw tokens, secrets, signed URLs, patient data, or health narratives.

No real patient data is permitted. Only named, least-privilege beta operations, security/privacy, and engineers with a documented QA need may access beta data. Artifact links must remain protected/expiring and may not be posted publicly.

## Cleanup operation

Dry-run from the repository root:

```powershell
python scripts/cleanup_artifacts.py --dry-run
```

Apply only after confirming the resolved artifact directory and retention configuration:

```powershell
python scripts/cleanup_artifacts.py
```

The script confines deletion to report/overlay files under the configured artifact root, skips symlinks, and honors modification time. Before GO, schedule it in private staging, alert on failure, verify provider backups/log retention, test expired links, and retain run evidence.

## Requests and incidents

Deletion requests go to `[DELETION/PRIVACY CONTACT]`. Authenticate proportionately, identify scoped records, delete eligible data, document exceptions, and confirm completion without collecting more personal information. For suspected exposure, pause beta access, restrict/revoke links/accounts, preserve minimum safe evidence, notify the private incident owner, assess required notification/deletion, remediate, and require a new go/no-go decision.
