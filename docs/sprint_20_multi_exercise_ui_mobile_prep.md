# Sprint 20 — Multi-Exercise UI and Mobile Preparation

## Goal and delivered scope

Sprint 20 gives the five existing rule-based analyzers a consistent product surface without adding an analyzer or promoting ML/DL. The web app now has an Exercise Library, API-backed manual selector, reusable recording guidance, consistent result status, session filters, and exercise-aware therapist summaries.

## Supported boundary

Supported: `bodyweight_squat`, `sit_to_stand`, `knee_extension`, `shoulder_abduction`, and `hip_abduction`. Planned and unavailable: `heel_raise`, `lunge`, `step_up`, `balance`, `walking_gait_screen`, `shoulder_flexion`, and `hip_flexion`.

`GET /api/v1/exercises` is the client catalog. `GET /api/v1/exercises/{exercise_id}` returns one entry or `EXERCISE_NOT_FOUND`. Supported records include their stable analyzer endpoint; planned records have `endpoint_path=null` and `supported_in_app=false`.

## UX behavior

- `/exercises` separates supported cards from disabled planned cards.
- `/analyze` permits only the five supported selections and shows view, landmarks, movement pattern, and safety notes.
- Rejected results show the rejection reason and recording guidance without a movement score or ML panel.
- Session history filters by exercise and status and sorts by date.
- The therapist prototype labels sessions and low-confidence groups by exercise.

## Safety and technical boundaries

Manual selection and rule-based analysis remain primary. Recognition and ML are experimental and cannot activate planned exercises or override validity. Text describes observed movement patterns, possible compensation, or limited observed range; it does not diagnose injury, weakness, pathology, or prescribe treatment.

## Validation

Run `python -m pytest`, then `cd frontend`, `npm test`, and `npm run build`. For manual review, start FastAPI and Vite, inspect `/exercises`, each Analyze selection, supported/rejected result fixtures, session filters, and the exercise metadata endpoints.
