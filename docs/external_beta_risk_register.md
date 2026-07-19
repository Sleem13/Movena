# External Closed Beta Risk Register

Severity is impact if realized; likelihood is the pre-mitigation estimate. Owners are accountable roles. `Blocked` means the beta cannot start until evidence exists.

| Risk | Severity | Likelihood | Mitigation | Owner | Status |
|---|---|---|---|---|---|
| Tester uploads real patient data | Critical | Possible | Explicit consent/onboarding warning, test-only protocol, least-privilege access, incident/deletion path | Privacy lead | Open |
| Tester interprets output clinically | Critical | Possible | Persistent disclaimer, limitations, careful result language, comprehension check, pause on misunderstanding | Safety lead | Open |
| Upload failure | High | Possible | Format/size preflight, progress, cancel/retry, physical-device network matrix | Mobile QA lead | Blocked |
| Backend downtime | High | Possible | Private monitoring, health check, outage template, rollback/disable plan | Backend/DevOps lead | Blocked |
| Artifact or privacy exposure | Critical | Unlikely | Signed/authorized temporary links, expiration/cleanup verification, access review, incident response | Security lead | Blocked |
| Movement score misinterpreted | High | Possible | “Not a clinical score,” suppress score for rejected/error input, usability check | Product safety lead | Partially mitigated |
| Low-confidence result misunderstood | High | Possible | Confidence explanation, warnings, rejected threshold, tester comprehension question | Analysis QA lead | Open |
| Unsupported exercise attempted | Medium | Likely | Fixed supported list, disabled planned exercises, manual selection warning | Product lead | Mitigated |
| Token/auth failure | High | Possible | Login/expiry/logout/revocation tests, protected artifact test | Backend/mobile lead | Blocked |
| App crash | High | Possible | Fail-closed remote URL config, automated regression, then physical launch/upload/result loops | Mobile QA lead | Blocked |
| Network interruption | Medium | Likely | Timeout/cancel/retry guidance; Wi-Fi/mobile-network tests without sensitive logs | Mobile QA lead | Open |
| Report/overlay link failure | Medium | Possible | Preview/download/expiry tests and non-clinical fallback copy | Backend QA lead | Open |
| Feedback not submitted | Medium | Possible | Short form, in-pack reminder, scheduled check-in, privacy-safe alias | Beta program lead | Open |
| Empty beta inputs misrepresented as successful results | High | Possible | Block Sprint 30 when required evidence has no genuine rows; use `not_available` for denominator-free rates | Product/QA lead | Active blocker |
| Second wave starts without first-wave evidence or closed P0/P1 gates | High | Possible | Require recorded Sprint 30 GO/CONDITIONAL GO, installed-build QA, active private channels, and consent before invitation | Beta program/release lead | Active blocker |
| Staging build silently targets local/placeholder API | High | Possible | Remote mobile environments reject missing, HTTP, and `.invalid` API URLs | Mobile release lead | Mitigated in code; build blocked |
| Source filename exposed in request logs | High | Unlikely | Squat upload log records content type only; review deployed provider logs | Privacy/security lead | Mitigated locally |

Review at build freeze, after each critical/high report, and before any decision to continue. A privacy/safety critical, blocker, or uncontrolled high risk is a stop condition.
