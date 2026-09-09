# Complete Care Clinical Goals and Recommendations

Updated: 2026-09-09

## Senior physiotherapist position

Complete Care should be positioned as a clinician-led rehabilitation support pathway, not as an autonomous treatment system. Its strongest clinical value is to help the treating physiotherapist see what happens between visits: exercise completion, visible movement quality, symptoms, confidence, barriers, appointment follow-through, and patient-reported progress.

The platform should help patients participate more consistently in their agreed plan and help physiotherapists review risk, response, adherence, and functional progress with better information. It must not diagnose conditions, prescribe independent treatment, clear a patient for activity, or replace clinical examination and reasoning.

## Clinical goal statement

The goal of Complete Care is to improve access, continuity, safety, and accountability in physiotherapist-guided rehabilitation by connecting the patient, therapist, exercise plan, movement-analysis records, symptom check-ins, appointments, reminders, and follow-up actions in one governed care workflow.

Every product decision should support four clinical outcomes:

1. Safer participation in the agreed rehabilitation plan.
2. Better adherence and confidence between supervised visits.
3. Earlier recognition of barriers, symptom escalation, and poor response.
4. Clearer therapist review, documentation, and shared decision-making.

## Priority clinical goals

### 1. Patient safety and clinical boundaries

The first goal is to keep the patient inside an appropriate clinical pathway. Complete Care should require clear consent, patient identity, assigned therapist ownership, plan context, and escalation rules before handling real patient data.

Recommendations:

- Require initial physiotherapist assessment before any patient-specific rehabilitation plan is activated.
- Keep red-flag screening, precautions, postoperative restrictions, referral decisions, and progression decisions under clinician control.
- Display stop-and-seek-help guidance wherever patients submit symptoms or exercise videos.
- Do not allow AI analysis, RehabRL, or coaching templates to change exercise selection, dosage, frequency, resistance, range, or precautions without therapist approval.
- Use "clinical follow-up required" and "urgent pathway" states for symptom escalation; do not ask the platform to decide whether a symptom is an emergency.

### 2. Function-first rehabilitation

The care pathway should focus on what matters to the patient: movement, participation, independence, confidence, return to work/sport/daily roles, and meaningful activity tolerance.

Recommendations:

- Capture one patient-stated functional goal at onboarding, such as walking stairs, returning to prayer positions, carrying groceries, sitting to standing safely, returning to sport, or tolerating a work shift.
- Tie exercise plans to functional goals, not only to exercise completion.
- Track patient-specific baseline and follow-up measures at clinically sensible intervals.
- Use movement-analysis data as supporting evidence, while preserving therapist interpretation of pain, irritability, strength, mobility, balance, endurance, and psychosocial context.

### 3. Adherence, confidence, and behavior support

Most rehabilitation fails quietly between visits. Complete Care should make adherence easier, reveal barriers earlier, and support realistic patient-owned goals.

Recommendations:

- Keep SMART goals patient-chosen or explicitly patient-agreed.
- Ask short check-in questions about pain response, difficulty, fatigue, confidence, sleep/energy, and barriers.
- Use reminders as opt-in support, not pressure.
- When confidence is low or barriers are reported, recommend therapist review or a smaller agreed step instead of generating new treatment advice.
- Separate general lifestyle coaching from clinical rehabilitation dosage.

### 4. Therapist review and decision support

The therapist dashboard should reduce cognitive load and make clinical review faster without hiding uncertainty.

Recommendations:

- Prioritize "needs review" items: worsening symptoms, repeated non-completion, high pain/difficulty, poor recording quality, low confidence analysis, missed appointments, and unacknowledged clinical follow-ups.
- Show trends over time instead of single-session scores as the primary review surface.
- Always show original recording access, analysis confidence, recording limitations, and exercise-plan context beside movement metrics.
- Provide approve, modify, reject, and supersede workflows for model-generated recommendation candidates.
- Maintain immutable audit history for plan changes, symptom escalation, therapist acknowledgements, consent, and privacy requests.

### 5. Measurement quality and clinical validity

Single-camera movement analysis is useful when it is conservative and transparent. It should help therapists ask better questions, not pretend to measure the whole clinical picture.

Recommendations:

- Reject or qualify poor recordings instead of producing confident-looking scores.
- Keep rule-based exercise analysis primary until each model passes exercise-specific validation.
- Validate each supported exercise separately across body sizes, clothing, lighting, camera placement, assistive devices, pain presentations, and relevant patient populations.
- Do not combine pose, sensor, questionnaire, and clinical data into a composite clinical score until the score has a defined construct, validation plan, and governance approval.
- Treat movement scores as educational observations unless a validated clinical scoring contract exists.

### 6. Equity, access, and usability

A complete care project should not only work for ideal users with perfect devices and high health literacy.

Recommendations:

- Keep Arabic and English workflows clinically equivalent, not just translated.
- Design for older adults, pain-limited users, low confidence with technology, weak networks, and shared family devices.
- Support low-bandwidth fallback for appointments and follow-ups.
- Provide printable or clinician-shareable summaries for patients who cannot rely on mobile access.
- Test patient comprehension of consent, safety wording, exercise instructions, and escalation messages before real-patient use.

## Recommended care workflow

1. Onboarding and consent: identity, role, consent, privacy notice, emergency limitations, assigned therapist, and patient profile.
2. Baseline physiotherapist assessment: diagnosis and clinical reasoning stay outside autonomous software logic; the therapist records goals, precautions, contraindications, baseline measures, and plan intent.
3. Plan activation: therapist assigns exercises, dosage, frequency, schedule, safety notes, and review date.
4. Patient execution: patient follows the agreed plan, records selected exercises when appropriate, and submits pain/difficulty/fatigue and comments.
5. Automated support: platform checks plan adherence, recording quality, movement-analysis confidence, symptom-change status, and missed check-ins.
6. Therapist review: therapist reviews exceptions, trends, and recordings; updates the plan only after clinical reasoning and patient agreement.
7. Escalation and referral: symptom concerns create accountable follow-up; urgent concerns show the organization-approved pathway and notify the therapist.
8. Outcomes review: patient and therapist review progress against functional goals and agreed outcome measures at defined intervals.

## Minimum clinical data set

For a safe Complete Care baseline, capture only what is clinically useful and governed:

- Patient goals, relevant diagnosis or care reason, current precautions, and contraindications.
- Therapist-assigned exercise plan with dosage, frequency, schedule, review date, and plan version.
- Patient-reported pain response, difficulty, fatigue, confidence, symptom change, and barriers.
- Adherence and completion status.
- Movement-analysis result, original recording reference, confidence, limitations, and recording quality.
- Therapist review status, acknowledgement, plan changes, and follow-up disposition.
- Validated outcome measures only when licensing, scoring, language, and interpretation workflows are defined.

## Launch recommendations

Complete Care should remain no-go for real-patient production use until these clinical conditions are met:

- Named clinical safety owner signs the intended-use statement, exclusions, safety copy, and escalation workflow.
- Physiotherapist review is completed for every supported exercise protocol, movement threshold, and patient-facing feedback phrase.
- Real-device testing confirms that patients can record safely, understand limitations, submit symptoms, join appointments, and receive follow-up instructions.
- Red-flag, postoperative, neurological, fall-risk, cardiopulmonary, and medically unstable presentations have explicit exclusion or supervised-use rules.
- Legal/privacy review confirms consent, retention, deletion, access control, incident response, and cross-border data handling.
- A pilot with therapists measures usability, review burden, false positives/negatives, missed escalations, patient comprehension, and workflow fit before expansion.

## Clinical recommendation summary

From a senior physiotherapist perspective, Complete Care is clinically promising if it remains a governed extension of therapist-led care. The safest and most useful version is not "AI tells the patient what to do." It is "the therapist and patient share a clearer picture of progress, barriers, symptoms, exercise quality, and next actions."

The immediate clinical priority should be a narrow, high-quality, therapist-reviewed pathway for assigned rehabilitation plans and monitored home exercise. Expand conditions, exercises, remote coaching, and AI decision support only after each component proves safe, understandable, measurable, and useful in real clinical workflow.

## Clinical sources reviewed

- World Health Organization, Rehabilitation fact sheet, 22 April 2024: https://www.who.int/news-room/fact-sheets/detail/rehabilitation
- World Health Organization, Rehabilitation programme: https://www.who.int/teams/noncommunicable-diseases/sensory-functions-disability-and-rehabilitation/rehabilitation
- World Health Organization, Rehabilitation 2030 initiative: https://www.who.int/initiatives/rehabilitation-2030
- World Health Organization, Package of interventions for rehabilitation: https://www.who.int/teams/noncommunicable-diseases/sensory-functions-disability-and-rehabilitation/rehabilitation/service-delivery/package-of-interventions-for-rehabilitation
- American Physical Therapy Association, Telerehabilitation in Physical Therapist Practice CPG, 21 March 2024: https://www.apta.org/patient-care/evidence-based-practice-resources/cpgs/telerehabilitation-pt-practice-apta-cpg
- American Physical Therapy Association, Clinical Practice Guidelines Library: https://www.apta.org/patient-care/evidence-based-practice-resources/cpgs
