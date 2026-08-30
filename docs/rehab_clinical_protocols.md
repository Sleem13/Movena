# Rehabilitation clinical protocol catalog

## Purpose and safety boundary

The rehabilitation workspace contains 26 clinician-facing condition pathways.
Each pathway includes aliases for search, red-flag screening prompts,
precautions, five criteria-based phases, treatment options, progression
criteria, outcome measures, and authoritative source links.

These pathways are clinical references. They do not diagnose a patient,
replace a physical examination, select dosage autonomously, or override
postoperative orders. Timelines are intentionally described as typical rather
than mandatory. Clinicians must adapt the plan to tissue irritability,
comorbidities, goals, setting, response over the following 24 hours, and shared
decision-making.

## Policy-supported versus reference-only conditions

The packaged RehabRL checkpoint has a fixed 32-element input: 12 injury labels,
five recovery stages, nine patient metrics, and six joint-angle features. Its 30
actions are also fixed. Changing the 12-label one-hot vector would invalidate
the checkpoint and misalign learned weights.

Therefore:

- The original 12 conditions can produce a `rehabrl_policy` response enriched
  with the matching clinical pathway.
- The 11 additional conditions produce a `protocol_reference` response with no
  action ID, Q-values, or model-confidence claim.
- Synthetic simulation remains available only for the original 12 trained
  labels.
- Expanding model coverage requires a new versioned state schema, retraining,
  calibration, external validation, subgroup safety analysis, and clinical
  approval.

## Current coverage

The catalog covers ACL injury, rotator-cuff tear, lumbar radiculopathy, lateral
ankle sprain, lateral elbow tendinopathy, patellofemoral pain, nonarthritic hip
pain, Achilles tendinopathy, rotator-cuff–related shoulder pain, plantar heel
pain, mechanical neck pain, hamstring strain, knee and hip osteoarthritis,
meniscal/cartilage lesions, adhesive capsulitis, carpal tunnel syndrome,
nonspecific low back pain, concussion/mild traumatic brain injury, stroke,
Parkinson disease, total knee arthroplasty, total hip arthroplasty, peripheral
vestibular hypofunction, older-adult fall risk, and osteoporosis.

The assessment's Low/Moderate/High indicator is a **load caution** derived from
normalized pain, fatigue, and severity inputs. It is not a medical risk score
and does not establish that red flags were screened. The API returns
`clinical_safety.red_flags_screened: false` and the UI keeps that limitation
visible beside the condition-specific screening prompts.

## API behavior

`GET /api/v1/rehab-rl/protocols` returns the detailed catalog. A single pathway
is available from `GET /api/v1/rehab-rl/protocols/{condition_id}`. The existing
exercise endpoint also returns lightweight `conditions` entries used by the
searchable combobox.

`POST /api/v1/rehab-rl/assessment` accepts `condition_id`. The legacy
`injury_type` field remains supported for the original 12 labels. Every response
includes `mode`, `protocol`, and the selected `phase_plan` so the UI can label
model output separately from evidence-informed reference material.

### Mandatory safety gate

Every assessment accepts a structured `safety_screen`. Policy inference and
treatment guidance remain locked until the clinician confirms that red flags
and precautions were reviewed and attests that the examined presentation fits
the pathway. Postoperative cases also require confirmation of the surgeon's
loading, range-of-motion, brace, and weight-bearing orders.

If a red flag is marked present, the response changes to `mode: safety_hold`
and `treatment_readiness: hold_and_refer`. No action, Q-values, exercise list,
or model-confidence score is returned. This is a workflow guard, not an
emergency triage system; organizations must configure their own referral and
emergency procedures.

Each protocol carries `evidence_reviewed_on`, `next_review_due`, and
`clinical_status` metadata so stale pathways can be detected and governed.

## MLOps inference contract

`GET /api/v1/rehab-rl/model-manifest` exposes the versioned state/action
contract, its SHA-256 fingerprint, the 12 trained labels, checkpoint
compatibility, intended use, exclusions, and pre-release monitoring
requirements. Inference compatibility requires the packaged 32-state,
30-action, 12-label contract. Expanded reference conditions cannot enter model
inference.

Before clinical release, the manifest requires external validation, subgroup
and calibration analysis, override/adverse-event monitoring, drift thresholds,
a rollback procedure, and documented clinical approval. These controls follow
the transparency and total-product-lifecycle direction in FDA/IMDRF good
machine learning practice guidance; they do not imply regulatory clearance.

Each assessment now creates a privacy-minimized, clinician-scoped decision
audit record. The governance summary reports decision volume, safety holds,
referral holds, decision modes, and current escalation configuration. Audit
records contain no patient identifier, free-text note, or raw clinical
measurement.

## Evidence governance

The source catalog links to current guideline hubs and primary clinical
practice guidelines from APTA Orthopedics, AAOS, Canadian Stroke Best
Practices, and the Parkinson's Foundation. Source dates and links should be
reviewed at least annually and whenever a new guideline is published. Content
changes should undergo physical therapist review and be versioned in release
notes.

Recommended next governance steps:

1. Assign a clinical owner and review date to each pathway.
2. Configure and clinically approve jurisdiction-specific emergency and referral instructions for every deployment.
3. Add structured contraindications from the patient's diagnoses, medications,
   surgery, and vital signs before enabling dosage support.
4. Validate outcome-measure licensing and electronic administration rules.
5. Pilot with therapists and add explicit override/adverse-event capture, then measure those signals and
   usability before patient-facing exposure.
