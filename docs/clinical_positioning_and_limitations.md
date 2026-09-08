# Clinical Positioning and Limitations

## Intended Positioning

Movena supports exercise monitoring and educational movement review. It can summarize visible movement patterns, repetitions, selected joint-angle estimates, input quality, and measurement confidence. It is not a diagnostic device, a substitute for examination, or an autonomous treatment-planning system.

With appropriate consent and access controls, it may help physiotherapists review exercise execution remotely. It should not be relied upon for high-risk patients, medically unstable users, or activities requiring close guarding without appropriate professional supervision and an approved care context.

## Appropriate Language

Use:

- “The recording shows…”
- “A possible movement pattern was observed…”
- “Consider reviewing camera placement or technique with your physiotherapist.”
- “Measurement confidence is low because key joints were not consistently visible.”

Avoid:

- “You have…” or “This confirms…”
- injury, pathology, impairment, prognosis, fall-risk, or recovery conclusions;
- treatment prescriptions or claims that one movement pattern caused pain;
- “clinically accurate,” “therapist replacement,” or similar claims without appropriate evidence and authorization.

## Measurement Limitations

Single-camera pose estimates are affected by view, camera height/tilt, distance, lighting, clothing, occlusion, frame rate, video edits, body proportions, assistive devices, and landmark-model errors. Two-dimensional angles do not represent full three-dimensional joint motion and cannot measure joint loading, pain, fatigue, or internal tissue stress. A movement score is an educational rule summary, not a health score.

Rule thresholds are exercise-, view-, and protocol-specific. Optional ML is experimental, trained on limited data, and cannot supersede the validity gate or rule-based observations. A confident model output can still be wrong.

ML/DL remains experimental unless a specific version passes documented promotion criteria and scope review. Even a promoted support model would not diagnose, prescribe treatment, or replace professional judgment. Low-confidence output should be reviewed manually rather than used for progression or clinical decisions.

## Patient-Facing Safety Wording

“Use this analysis for exercise monitoring and educational support only. It does not replace assessment, diagnosis, or treatment by a licensed physiotherapist or healthcare professional. Stop the exercise if pain increases or if you feel dizzy, faint, unusually short of breath, unstable, or otherwise unwell. Seek appropriate professional or urgent help for concerning symptoms.”

The product should not algorithmically determine whether symptoms are an emergency. Local urgent/emergency guidance belongs in product support content appropriate to the deployment region.

## Professional Use

Therapists should review the original recording, protocol, patient context, validity, visibility, confidence, and limitations before using measurements as supporting information. Decisions about diagnosis, progression, regression, precautions, referral, or treatment remain with appropriately licensed professionals.
