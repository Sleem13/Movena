# Sprint 31 Second-Wave Regression Checklist

| Gate | Current result | Required evidence |
|---|---|---|
| Backend `/health` | Pass in prior staging check | Fresh HTTPS 200 before invite |
| Backend `/ready` | Pass in prior staging check | Fresh HTTPS 200 with database ready |
| `/api/v1/exercises` | Pass in prior staging check | Five supported exercises only |
| Android build installs | Blocked | Post-fix APK installed on named device |
| App opens | Blocked | Cold/warm launch evidence |
| Safety disclaimer visible | Blocked on device | Screenshot/check without patient data |
| Auth works | Blocked on device | Login, expiry, logout/login |
| Valid upload works | Blocked on device | Non-identifying fixture succeeds |
| Invalid/static rejection | Blocked on device | Rejected safely |
| No fake rejected score | Blocked on device | `movement_score=null`, ML skipped/not applicable |
| Private links active | Blocked | Access-tested feedback/support/privacy destinations |
| Known limitations visible | Blocked on device | In-app navigation check |

Any failed P0/P1 row prevents invitation.

