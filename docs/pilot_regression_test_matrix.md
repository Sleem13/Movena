# Pilot Regression Test Matrix

Statuses are `pass`, `fail`, `blocked`, or `not tested`. A pass marked automated does not replace physical-device validation.

| Scenario | Status | Evidence / remaining gate |
|---|---|---|
| App opens | blocked | No installed Android stability build or physical-device run |
| Safety disclaimer visible | pass | Mobile source/unit and web result regression; installed-build visibility still blocked |
| Exercise Library loads | pass | Backend metadata/API and web/mobile registry automation |
| Each supported exercise opens | blocked | Automated routes/guidance pass; exact mobile build navigation not physically tested |
| Camera guidance per exercise | pass | Five-exercise mobile camera-guidance regression coverage |
| Video picker | blocked | Source flow exists; physical permission/picker behavior not run |
| Upload valid video | blocked | API/unit flows pass; deployed device-to-staging upload absent |
| Upload invalid/static video | pass | Backend validity/rejection regression coverage; device display still blocked |
| Retry failed upload | pass | Retained selection and synchronous double-submit guard unit coverage |
| Backend offline | pass | Friendly network/timeout parsing and retry coverage; real Wi-Fi interruption blocked |
| Expired token | pass | SecureStore clearing and friendly session-expiry automation |
| Rejected result | pass | Not-scored, zero-rep, null score/breakdown, retry, guidance, and safety-copy coverage |
| Session history when enabled | pass | Backend/web/mobile automated contract coverage; deployed device check blocked |
| Report/overlay links when enabled | pass | Missing URL UI, standardized private 404, signed URL, and frontend preview/download automation; deployed playback blocked |

Overall: automated stability coverage passes, but end-to-end private staging and physical-device rows keep the pilot gate **blocked**.
