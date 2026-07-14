# Therapist Dashboard Roadmap

## Intended Role

The dashboard organizes movement-monitoring sessions for professional review. It supports, but never substitutes for, clinical assessment, diagnosis, treatment planning, or escalation decisions.

## Phase 1 - Read-Only Review Prototype

- Therapist login after identity and role authorization exist.
- Patient/session list using synthetic or consented test data.
- Patient profile with consent scope and assigned exercise program.
- Session summary, original/annotated media, quality/confidence, detected observations, feedback, and report download.
- Clear distinction between patient-entered context, rule observations, and experimental ML.

## Phase 2 - Exercise Planning

- Exercise catalog and plan templates.
- Sets/reps/frequency recorded as therapist-entered instructions, not AI prescriptions.
- Assignment status, due windows, completion state, and patient questions.

## Phase 3 - Longitudinal Review

- Trends in repetitions, measured angles, confidence, and completion.
- Movement-score trends with protocol/quality caveats, detected-observation history, and adherence tracking.
- Filters by exercise, camera view, recording quality, and date.
- Comparisons suppressed when input quality or protocol differs materially.

## Phase 4 - Collaboration and Governance

- Therapist notes, review status, patient-visible comments, amendment history, and audit events.
- PDF export with analysis versions, confidence, limitations, and disclaimer.
- Role-based access, clinic tenancy, consent scope, break-glass policy, and export/delete workflows.

## Release Gates

Authentication and authorization testing, privacy impact assessment, usability testing with physiotherapists, accessibility review, retention policy, and incident-response ownership are required before real patient use.
