# Recovery & Lifestyle Coaching

## Purpose

Recovery & Lifestyle Coaching connects a patient’s rehabilitation plan with patient-chosen behavior goals. It supports reflection, confidence, participation, and accountability between clinical visits. It is not a diagnostic, prescribing, psychotherapy, nutrition-prescribing, crisis, or emergency service.

The module is deliberately rules-based. It does not use a language model to generate health advice, and it never changes a rehabilitation prescription autonomously.

## Clinical scope

Supported coaching domains are:

- Mobility routine and rehabilitation-plan adherence
- General activity and participation
- Sleep routine (behavioral routine only, not sleep-disorder treatment)
- Stress-management habits (not psychotherapy)
- Social support, access, and environmental barriers

Every goal must be specific, measurable, time-bound, chosen or explicitly accepted by the patient, and acknowledged as coaching rather than clinical care. Therapist-authored action plans require documented patient agreement.

The module must not:

- Diagnose a condition or interpret symptoms as a diagnosis.
- Start, stop, or change medication, exercise dosage, postoperative restrictions, or treatment.
- Provide individualized meal plans, psychotherapy, or emergency counselling.
- Override the treating clinician’s plan, precautions, red flags, or local escalation policy.
- Present check-in ratings as validated clinical outcome measures.

## Safety workflow

Check-ins collect energy, sleep quality, stress, recovery confidence, activity minutes, barriers, symptom-change status, and urgent-concern status. The 1–5 ratings are non-diagnostic reflections.

The server assigns one deterministic state:

| State | Trigger | Product response |
|---|---|---|
| `ready` | No safety concern or material barrier | Support the agreed next step |
| `review_plan` | Low confidence or a reported barrier | Suggest a smaller agreed step and therapist review when appropriate |
| `clinical_follow_up` | New or worsening symptoms | Do not adapt treatment; notify the therapist and request clinical review |
| `urgent_escalation` | Immediate safety or health concern | Pause coaching, show the configured urgent/emergency instruction, and notify the therapist |

The application is not an emergency-response system and does not guarantee real-time clinician monitoring. Deployments must configure `CLINICAL_ORGANIZATION_NAME`, `CLINICAL_ESCALATION_CONTACT`, and `CLINICAL_ESCALATION_INSTRUCTION` to match an approved local workflow.

## Roles and access

- Patients can view their own dashboard, create patient-agreed goals, record check-ins, and update their own goal progress.
- Therapists can access assigned patients, review goals and check-ins, and create patient-agreed action plans.
- Administrators and super administrators use the same protected clinical access rules.
- Anonymous users and clinicians without an assignment cannot access patient coaching records.

Goal, check-in, action-plan, and update events are written to the audit log. Escalating check-ins also create therapist notifications. Access enforcement occurs on the API; the UI is not the security boundary.

Clinical follow-up remains pending until an assigned clinical user acknowledges it with an attested disposition. Urgent records cannot be closed as "no additional action." The acknowledgement is immutable, audited, and visible to the patient. Organizations must define their escalation organization and contact before staging or production startup, and must establish their own review expectations without presenting the service as real-time monitoring.

Patients may explicitly opt in to approximate daily or weekday reminders. The periodic notification worker sends one deduplicated patient reminder per due day and, after the configured number of missed days, one routine therapist follow-up per week. Disabling reminders does not disable symptom alerts created by a submitted check-in.

The trend workspace charts longitudinal sleep, confidence, stress, energy, and activity reflections. Informal 1-5 coaching ratings are labeled non-diagnostic and are not mixed with, scored as, or represented as validated patient-reported outcome measures (PROMs). Validated instruments require a separate licensed/approved implementation, scoring contract, provenance, and clinical interpretation workflow.

Five therapist-reviewed behavior-goal templates cover general rehabilitation adherence, orthopedic participation, neurologic support, persistent-symptom pacing, and sleep routine. Templates never prescribe exercise selection, dosage, postoperative progression, or treatment changes, and the patient must choose or explicitly accept the resulting goal.

## API

All endpoints are under `/api/v1/recovery-coaching` and require an authenticated patient or clinical role.

| Method | Endpoint | Purpose |
|---|---|---|
| `GET` | `/dashboard` | Patient-scoped summary, goals, check-ins, action plans, and safety copy |
| `GET` | `/templates` | Read bounded behavior-goal templates and clinical-review rules |
| `POST` | `/goals` | Create a patient-agreed SMART goal |
| `PATCH` | `/goals/{goal_id}` | Update progress and lifecycle status |
| `POST` | `/check-ins` | Record a reflection and compute the deterministic coaching state |
| `POST` | `/check-ins/{check_in_id}/acknowledge` | Clinician attestation and immutable follow-up disposition |
| `PUT` | `/reminder-preference` | Save patient-agreed reminder and missed-follow-up preferences |
| `POST` | `/action-plans` | Create a therapist-reviewed, patient-agreed action plan |
| `PATCH` | `/action-plans/{action_plan_id}` | Update action-plan status |

Clinical roles pass `patient_id` as a query parameter. Patient accounts are always resolved to their own profile regardless of client input.

## Persistence and deployment

Migration `0005_recovery_coaching` creates the coaching records. Migration `0006_coaching_follow_up` adds reminder preferences and clinical acknowledgement fields. Apply all revisions before deploying:

```powershell
.\.venv\Scripts\python.exe -m alembic upgrade head
```

Run `scripts/process_notifications.py` on a recurring worker schedule to enqueue due reminders and routine missed-check-in follow-ups. Worker execution frequency affects delivery latency and must not be described as a guaranteed response time.

Treat coaching entries as health-related patient records under the platform’s retention, privacy, export, deletion, backup, and incident-response policies. Do not place patient narratives in model telemetry or public client configuration.

## Clinical review basis

The boundary follows the American Physical Therapy Association’s recognition of physical therapists’ role in prevention, wellness, fitness, health promotion, and management of disease and disability, while preserving referral and scope limits. The coaching relationship and exclusions also align with the National Board for Health & Wellness Coaching scope and ethics. General activity content must remain compatible with the patient’s abilities and clinician guidance, consistent with CDC disability and physical-activity guidance.

- [APTA: Physical Therapist's Role in Prevention, Wellness, Fitness, Health Promotion, and Management of Disease and Disability](https://www.apta.org/apta-and-you/leadership-and-governance/policies/pt-role-advocacy)
- [APTA: Prevention and Wellness](https://www.apta.org/patient-care/public-health-population-care/prevention-and-wellness)
- [NBHWC Scope of Practice](https://nbhwc.org/scope-of-practice/)
- [NBHWC Code of Ethics](https://nbhwc.org/code-of-ethics-and-professional-conduct/)
- [CDC: Physical Activity for People with Disability](https://www.cdc.gov/disability-and-health/conditions/physical-activity.html)

This implementation still requires review by the deployment organization’s licensed clinical lead, privacy officer, and legal/compliance team before production use.
