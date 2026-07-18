# Internal Pilot Issue Tracking

| Severity | Definition | Response |
|---|---|---|
| Blocker | Data exposure, auth bypass, unsafe/misleading result, app cannot complete core flow | Stop affected testing immediately; owner triage now |
| High | Major supported flow consistently fails or incorrect result state without immediate safety exposure | Triage same working day; block release if unresolved |
| Medium | Recoverable functional/usability issue with workaround | Prioritize in sprint and regression-test fix |
| Low | Cosmetic, copy, or minor inconvenience | Backlog with evidence |
| Safety/privacy | Any clinical-claim, consent, personal-data, token, artifact, or unsafe-guidance concern | Treat at least high; notify safety/privacy owner immediately |

Record a non-identifying issue ID, timestamp, build/backend versions, platform/device, exercise, expected/actual result, reproducible steps, sanitized logs, severity, owner, status, fix, regression test, and closure approval. Never paste credentials, signed URLs, patient data, or raw media into a general issue tracker.
