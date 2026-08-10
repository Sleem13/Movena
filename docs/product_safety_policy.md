# Product Safety Policy

## Sprint 29E first-wave boundary

No tester begins before genuine consent is recorded. Only the eight registered analyzers and non-identifying test videos are allowed. Real patient data, clinical use, diagnosis/treatment claims, public release, unsupported exercises, and recognition-as-form-evidence are prohibited. Any patient data, privacy/artifact exposure, diagnostic wording, fake rejected score, launch crash, or majority upload failure pauses the beta.

## Sprint 31 second-wave boundary

The second wave is NO-GO while Sprint 30 lacks real results and P0/P1 operational gates remain unresolved. Do not invite, assign, or activate second-wave testers. Any future wave is limited to trusted non-clinical adults using non-identifying tester-owned media, with consent completed first and immediate pause for patient data, privacy/artifact exposure, diagnostic wording, fake rejected scores, launch crashes, or majority upload failure.

## Sprint 30 evidence boundary

Sprint 30 is blocked because the external beta inputs contain headers only. No safety, privacy, reliability, comprehension, or clinical conclusion may be drawn from zero records. Continue Sprint 29B under the existing invitation, consent, no-real-patient-data, pause/stop, and escalation controls. No beta expansion or public release is authorized.

## Sprint 29B first-wave boundary

Sprint 29B is **NO-GO** and no tester may be invited. A future first wave is limited to 3–5 trusted non-clinical testers using aliases and approved non-identifying test videos. There is no public release, real-patient use, clinical validation, diagnosis/treatment claim, unsupported exercise, or ML/DL promotion.

Physical-device proof must confirm auth warnings do not leak into account screens, invalid/static inputs are rejected with no fake score, and safety/limitations remain visible. Feedback, issue, support, privacy/deletion, incident, consent, and limitations channels must be private, staffed, access-tested, and approved. Any patient-identifiable upload, privacy/security incident, diagnostic wording, public artifact, fake rejected score, majority upload failure, or launch crash pauses testing immediately.

## Sprint 29 execution boundary

Sprint 29 assets are being prepared, but actual external beta execution has not started and remains blocked. No tester may be invited, consented, assigned, or allowed to upload until private staging, Android build/install, physical-device QA, private feedback/support/privacy links, and release approval are complete.

Any future run is invite-only and non-public, uses non-identifying test videos only, and excludes real patients and sensitive health information. Feedback is product QA—not clinical validation, diagnosis, or treatment evaluation. Empty roster, feedback, and issue files must be reported as `not_started`, never interpreted as safety or reliability evidence. Safety/privacy flags require immediate pause and restricted review.

## Sprint 28 launch-candidate boundary

`0.28.0-rc.1` is an invite-only engineering candidate under `NO-GO`, not a public release or medical device. Tester-facing copy must state test videos only, no real patient-identifiable or sensitive health data, possible inaccuracy, and no diagnosis/treatment prescription/emergency use. Stop for pain, dizziness, numbness, instability, unusual discomfort, chest symptoms, or unusual shortness of breath and seek appropriate professional or urgent review.

Remote mobile builds must fail closed without a real private HTTPS API; upload logs must not include source filenames, tokens, secrets, media, or signed artifact URLs. Rule-based validity and rejection remain primary, rejected/error inputs receive no normal score, and experimental ML/DL/recognition cannot override safety gates.

## Sprint 27 external-beta boundary

External-beta preparation does not authorize external use. Any future run is invite-only, uses tester-owned non-identifying test videos or approved fixtures, excludes real patients and sensitive/identifiable health data, and evaluates product QA—not clinical validity. Consent/privacy and limitations must be acknowledged, access must be revocable, and safety/privacy critical or blocker issues pause testing.

Allowed language includes exercise monitoring, observed movement pattern, possible compensation, limited observed range, low confidence, and recording-quality effects. Diagnosis, injury/weakness detection, treatment/prescription, medical-device status, clinical validation, and emergency-use claims are prohibited. Scores are not clinical scores; rejected input receives no normal movement score. Rule-based validity/safety gates remain primary, and experimental ML/DL or recognition cannot override them.

## Sprint 26 stability-release boundary

PhysioVision AI supports exercise monitoring and does not replace assessment by a licensed physiotherapist. Product copy may describe an observed movement pattern, possible compensation, limited observed range, or low confidence and may suggest professional review. It must not state or imply diagnosis, injury detection, weakness detection, a treatment plan, medical-device status, or clinical validation.

Stability automation is not participant or clinical evidence. A zero-issue empty pilot log cannot be interpreted as safety validation. Missing disclaimers, a normal score on rejected input, artifact/token exposure, or diagnosis/treatment wording remains a stop-testing issue.

## Sprint 25 feedback boundary

Internal pilot feedback evaluates product usability, reliability, messaging, and privacy controls only. It must not solicit diagnoses, treatment outcomes, clinical histories, pain scores, or real patient media. Feedback does not establish clinical validity, model accuracy for care, or treatment effectiveness. Blocker and safety/privacy concerns stop the affected test until reviewed.

Only the five supported exercises may be tested. The pilot cannot promote experimental ML/DL or exercise recognition, and those layers cannot override rule-based validity/rejection behavior. Testers may voluntarily share restricted debugging evidence only after explicit notice; general feedback and issue logs contain no raw media, tokens, signed URLs, or patient identifiers.

## Internal pilot gate

Internal pilot documentation does not authorize pilot execution. Testing may start only after private staging, authenticated artifact handling, physical-device QA, privacy/security approval, and versioned safety-consent acknowledgment pass. Testers use non-identifying test media only and must never rely on results for diagnosis or treatment.

## Controlled staging boundary

Staging is restricted to internal staff and synthetic/non-identifiable recordings. A staging deployment, database, report, overlay, or mobile build is not clinical validation or pilot approval. Rule-based analyzers remain primary; experimental ML/DL and recognition cannot be promoted by deployment. External testing requires the documented privacy, consent, security, artifact, physical-device, and professional-review gates.

## Multi-exercise interface boundary

The Exercise Library must clearly separate supported analyzers from planned exercises. Planned cards are disabled and use “Planned — not available yet.” Metadata availability does not establish clinical validation. Product copy should use “observed movement pattern,” “possible compensation,” and “limited observed range,” never “injury detected” or “weakness detected.” For pain, worsening symptoms, or unusual symptoms, advise stopping the activity and seeking appropriate professional review rather than generating a diagnosis or treatment instruction.

## Mobile boundary

The mobile client records or selects media and uploads it for backend-side analysis; it does not run on-device pose estimation or make offline clinical inferences. Permission denial must fail clearly. Rejected inputs must not show a score. Tokens belong in platform secure storage, videos must not be retained on-device by the app beyond normal picker/camera behavior, and real patient-identifiable information is prohibited until production consent, privacy, retention, and security controls are approved.

Internal development builds must retain the same boundary during offline, timeout, interrupted upload, expired-token, and backend-error states. Retry may retain a local picker URI for user convenience, but logs must never include tokens, raw media, patient identifiers, or health details. EAS/cloud readiness does not authorize public distribution.

## Scope

PhysioVision AI provides educational movement-monitoring support. It does not diagnose injury or disease, determine fitness for activity, prescribe or modify treatment, or replace a licensed physiotherapist or other healthcare professional.

## Non-Negotiable Behaviors

- Reject static, invalid, zero-rep, or insufficient-visibility recordings rather than assign a normal movement score.
- Show pose quality, analysis confidence, limitations, and camera-view constraints with results.
- Warn clearly when confidence is low and recommend camera correction or professional review rather than over-interpreting the result.
- Keep experimental ML subordinate to validity and rule-based analysis; it cannot override rejection or safety messaging.
- Use observational wording such as “possible,” “may,” and “review,” not diagnostic labels.
- Do not infer pain, injury, pathology, recovery, fall risk, or treatment need from pose landmarks.
- Avoid logging raw media, personal identifiers, tokens, or health details.

## Camera and 2D Pose Limitations

Single-camera 2D pose estimates are affected by camera view, height, tilt, distance, lighting, clothing, occlusion, frame rate, video edits, and landmark errors. They do not measure full three-dimensional joint motion, force, tissue load, pain, or pathology. Front and side recordings support different observations, and an unsupported view must reduce confidence or cause rejection rather than produce a stronger claim.

## Stop and Seek Guidance

Users should stop the activity if pain increases, or if they experience dizziness, faintness, chest discomfort, unusual shortness of breath, new weakness/numbness, instability, or another concerning symptom. Urgent or severe symptoms require appropriate local urgent or emergency care. Product messaging must not attempt to triage emergencies algorithmically.

## Suggested UI Safety Messages

- “Stop if you feel pain, dizziness, or unusual discomfort.”
- “This feedback is for exercise monitoring and educational support only.”
- “Consult a licensed physiotherapist for clinical decisions.”
- “Low-confidence results should be reviewed manually.”

## Professional Review

Therapist review is preferred for clinical decisions, persistent symptoms, uncertain technique, low-confidence recordings, and exercise progression. Reports must retain their timestamp, exercise, analysis version, confidence, limitations, and disclaimer.

## Change Control

Each exercise, threshold, feedback rule, model, and user-facing safety statement requires versioning, regression tests, expert review, and rollback. Product release approval and clinical research approval are separate decisions.

ML/DL predictions are experimental unless a model has passed documented promotion criteria. They must remain visibly subordinate to the validity gate and primary rule-based biomechanics. Low-confidence analyses require manual review and must not be presented as reliable clinical conclusions.

## Knee-extension boundary

The system may describe visible extension range, complete cycles, tempo consistency, landmark visibility, and possible trunk movement. It must not infer joint stiffness, muscle weakness, pain, injury, passive range, safe resistance, or treatment progression.

## Shoulder-abduction boundary

The system may describe visible arm-raise range, complete cycles, tempo consistency, landmark visibility, possible trunk movement, and possible upward shoulder movement. It must not infer impingement, frozen shoulder, rotator-cuff weakness, injury, pain source, passive range, or treatment suitability.

## Hip-abduction boundary

The system may describe visible lateral leg range, complete cycles, tempo consistency, landmark visibility, possible trunk lean, and possible upward pelvic movement. It must not infer hip or gluteal weakness, instability, injury, pain source, balance capacity, passive range, or treatment suitability.
# Deployment privacy boundary

Deployment readiness does not imply clinical or patient-data readiness. Without authentication, authorization, consent, encryption governance, retention controls, and formal privacy/security review, this MVP must use synthetic or non-identifiable evaluation data only. Movement outputs are educational support and must not be represented as diagnosis or prescribed treatment.

Authentication controls access but does not validate clinical use, professional identity, consent, or appropriateness of an exercise. Role labels never grant clinical authority, and the development therapist dashboard is not a medical record.

Dataset availability, taxonomy mapping, model training, and app integration are separate gates. Unknown or weak labels require manual review, incompatible modalities cannot enter a pipeline, and no ML/DL model may automatically become an app or clinical output.

## Exercise-recognition boundary

Exercise recognition is an experimental routing aid, not clinical interpretation. It must never overwrite explicit selection, automatically invoke an analyzer, or provide feedback for an unsupported exercise. Suggestions require confirmation; absent or low-confidence output falls back to manual selection. Recognition confidence thresholds are product thresholds, not clinical safety thresholds.
