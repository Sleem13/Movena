# Sprint 26 Stability Fix Scope

## Allowed now

Upload retry/double-submit behavior, timeout and network copy, rejected-result display, token-expiry behavior, safety disclaimer visibility, camera guidance, temporary artifact handling, crashes, standardized backend errors, session-history display defects, and staging configuration are in scope.

## Explicitly excluded

No new exercise analyzer, ML/DL training or promotion, exercise-recognition promotion, public release feature, clinical claim, patient workflow, real patient data, or on-device pose/ML analysis is authorized.

## Implemented preventive fixes

1. Added a synchronous upload submission guard so two taps in the same React render cannot start two requests.
2. Added simple exercise-specific mobile camera and rejected-result retry guidance for all five supported exercises.
3. Added friendly mobile handling for `ARTIFACT_NOT_FOUND`, missing file, unsupported exercise, and processing errors without filesystem or token disclosure.
4. Added device count/model coverage and safer partial-row parsing to the pilot summary.
5. Standardized the required licensed-physiotherapist disclaimer across mobile and web results.
6. Added backend regression coverage confirming report/overlay 404 responses use `ARTIFACT_NOT_FOUND` and expose no filesystem path.

## Verified existing behavior

Upload progress, retained video/exercise retry, cancellation, timeout/network messages, file validation, SecureStore tokens, token attachment/expiry clearing/logout, rejected score suppression, null breakdown handling, zero reps, ML not-applicable behavior, missing artifact buttons, signed artifact authorization, and route-level processing-error responses were already present. No analyzer or scoring logic changed.
