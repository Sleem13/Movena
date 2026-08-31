# Closed-loop exercise response review

## Clinical purpose

The exercise check-in connects patient-reported response to therapist review without allowing the software to diagnose, prescribe, progress, or regress treatment. It complements movement-analysis observations; it does not convert them into clinical decisions.

The workflow records pain before and after, difficulty, fatigue, perceived effort (0–10), new or worsening symptoms, whether the patient stopped, optional symptom categories, and a free-text note. A patient reporting symptoms must acknowledge that the check-in is not monitored in real time and is not urgent care.

## Conservative response states

- `within_reported_tolerance`: no configured pain threshold, symptom-change flag, stopped-due-to-symptoms flag, symptom category, or very-high-effort flag was recorded. The message still states that progression is not authorized.
- `clinical_follow_up`: the record crossed a configured pain threshold, contained a symptom/stopping flag, or reported effort of 9–10. The message tells the patient not to progress, to contact the treating clinician, and to seek appropriate urgent help for severe or concerning symptoms.

The state is a workflow priority, not a diagnosis, emergency determination, tissue-safety assessment, or treatment recommendation.

## Therapist accountability

Assigned therapists receive a deduplicated review notification. A flagged response stays in the review queue until a therapist records one of the bounded dispositions, optionally documents a note, and explicitly attests that clinical judgment was used. A no-change disposition requires a rationale. The acknowledgement is retained in the audit log.

## Measurement boundary

Perceived effort and symptom responses are patient-reported session context. They are not standardized patient-reported outcome measures (PROMs). Validated, population-appropriate outcome measures should be selected and interpreted by the treating physiotherapist and tracked separately at baseline, reassessment, and discharge.

## Known limitations

- Self-report may be incomplete or misunderstood.
- A low symptom score does not prove that an exercise or dosage is safe.
- A high score does not establish diagnosis, severity, prognosis, or causation.
- Notifications do not guarantee immediate review.
- Local escalation instructions and contact details must be configured and operationally tested.
