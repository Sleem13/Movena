# Full Product Roadmap

## Phase 1 - Squat Analyzer MVP (Current)

Maintain the working squat upload, rule-based biomechanics, validity gate, repetition counting, confidence scoring, overlay/PDF generation, optional experimental ML second opinion, and responsive web dashboard. Freeze its API contract while architectural seams are introduced.

## Phase 2 - Product Foundation

- Define the exercise-engine interface and catalog without migrating behavior prematurely.
- Plan user profiles, patient/therapist roles, session history, PostgreSQL persistence, media storage, and stored reports.
- Complete manual annotations, participant grouping, dataset provenance, and model governance.
- Introduce persistence only after privacy, authorization, consent, deletion, and retention requirements are approved.

**Exit gate:** existing squat regression suite passes; no API behavior drift; data-governance review complete.

## Phase 3 - Multi-Exercise Engine

Add exercises one at a time through the registry: sit-to-stand, knee extension, shoulder abduction, hip abduction, balance, then gait/walking screening. Each receives dedicated data, recording instructions, validity, phases, thresholds, feedback, and tests. Sit-to-stand is the first pilot; squat thresholds are not reused.

**Exit gate:** exercise-specific tests, expert threshold review, bounded pilot evidence, and explicit limitations.

## Phase 4 - Therapist Dashboard

Add therapist login, patient list/profile, exercise assignment, session review, progress and adherence tracking, confidence warnings, detected-observation history, notes, and PDF export. This phase requires authentication, authorization, tenancy boundaries, and privacy review.

## Phase 5 - Mobile App

Ship a React Native + Expo client, with Flutter retained as an alternative if future staffing justifies it. The mobile app captures/uploads video, displays session results and exercise programs, provides history and therapist sharing, and retains safety notices. Backend-side analysis remains the initial architecture.

## Phase 6 - Validation and Deployment

Complete manual annotations and participant-grouped evaluation; publish model cards and limitations; conduct safety, privacy, and security review; deploy the web/backend stack to approved cloud infrastructure; and establish backups, incident response, accessibility, performance, and cost controls. Experimental ML may be promoted only through the model-promotion policy. Production deployment remains distinct from clinical validation.
# Sprint 9 Delivery Note

The product now supports two selectable rule-based movements: bodyweight squat and sit-to-stand. Sit-to-stand ML is explicitly unavailable, and the new analyzer remains an engineering prototype pending real-video, participant, and PT-informed threshold validation. No additional exercise should be activated until this validation is complete.
