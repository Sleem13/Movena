# External Beta Final QA Matrix

Status date: 2026-07-18. `Pass` means local automation or repository inspection only unless device/deployment evidence is named. `Blocked` items prevent beta launch.

| Area | Check | Status | Evidence / next action |
|---|---|---|---|
| Backend | `/health` contract | Pass | Automated test; repeat on HTTPS staging |
| Backend | `/ready` dependency status and 503 behavior | Pass | Automated test; repeat against managed DB/artifacts |
| Backend | Auth login/current-user/error contract | Pass | Automated tests; physical token lifecycle still blocked |
| Backend | `/api/v1/exercises` metadata | Pass | Automated tests |
| Backend | Upload size/type/empty/filename validation | Pass | Automated tests |
| Backend | Bodyweight squat analyze | Pass | Automated tests |
| Backend | Sit-to-stand analyze | Pass | Automated tests |
| Backend | Knee-extension analyze | Pass | Automated tests |
| Backend | Shoulder-abduction analyze | Pass | Automated tests |
| Backend | Hip-abduction analyze | Pass | Automated tests |
| Backend | Rejected result has no normal score/ML promotion | Pass | Validity/response/mobile tests |
| Backend | Session save/ownership | Pass | Automated tests; staging DB exercise blocked |
| Backend | Protected report/overlay links and clean 404 | Pass | Automated tests; deployed exposure review blocked |
| Backend | Artifact cleanup dry-run | Pass | 0 files/0 bytes eligible on 2026-07-18 |
| Mobile | Private APK install | Blocked | No EAS build submitted |
| Mobile | App startup | Blocked | TypeScript/tests pass; needs physical launch |
| Mobile | Consent/safety visible | Pass | Source/copy tests; legal approval blocked |
| Mobile | Exercise library loading/offline retry | Pass | Implementation/tests; device network test blocked |
| Mobile | All five supported exercise details | Pass | Registry/metadata tests |
| Mobile | Planned exercises disabled | Pass | Existing UI behavior/tests |
| Mobile | Camera permission denied | Pass | Explicit state implemented; physical settings flow blocked |
| Mobile | Video picker/unsupported file | Pass | Validation/tests; OEM picker coverage blocked |
| Mobile | Valid upload/progress | Blocked | Implementation/tests; private backend/device evidence missing |
| Mobile | Invalid/static upload rejected safely | Pass | Backend/mobile regression; device evidence blocked |
| Mobile | Retry failed upload | Pass | Tests; physical network exercise blocked |
| Mobile | Network interruption/timeout/cancel | Pass | Tests; physical exercise blocked |
| Mobile | Expired token | Pass | Tests clear secure token; deployed lifecycle blocked |
| Mobile | Logout/login | Pass | Tests/source; physical account flow blocked |
| Mobile | Success/rejected/error result clarity | Pass | Copy/parsing tests; external comprehension unknown |
| Mobile | Known limitations link | Pass | Added to onboarding/library/results |
| Mobile | Feedback/report-issue link | Blocked | Invitation placeholders have no active private URLs |
| Web | App loads and production build | Pass | Local automated build; no staging web deployment |
| Web | Exercise library/auth/upload/result/history | Pass | Automated tests; deployed smoke blocked |
| Security/privacy | Test data only/no real patient data | Pass | Policy and templates; operational enforcement requires onboarding |
| Security/privacy | No public artifact exposure | Blocked | Signed/auth design passes tests; staging exposure test missing |
| Security/privacy | Restricted HTTPS CORS | Pass | Fail-closed config tests; deployed origin missing |
| Security/privacy | Strong non-default secret | Pass | Fail-closed config tests; real secret provisioning blocked |
| Security/privacy | Secure mobile token storage | Pass | SecureStore tests; physical lifecycle blocked |
| Security/privacy | No source filename in squat request log | Pass | Privacy regression test |
| Safety | No diagnosis/treatment/clinical-validation claims | Pass | Copy audit; statements are explicit prohibitions/limitations |
| Release | Feedback/support/deletion contacts active | Blocked | Placeholders unresolved |
| Release | Multi-owner go/no-go signed | Blocked | Current decision is NO-GO |

Summary: repository automation and candidate fixes are strong, but the executable external-beta path is blocked by staging, build/install, device, artifact exposure, support-link, and approval evidence.
