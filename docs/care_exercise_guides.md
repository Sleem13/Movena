# Guided exercise expansion

## Instructions for existing analyzers

All 12 analyzer-supported exercises also have bilingual, three-step instructions,
therapist-directed dosage guidance and external references in
`backend/app/exercises/supported_guidance.json`. The metadata API and web fallback
catalog use this same file. Guidance is displayed independently from analyzer
availability, so adding instructions does not remove recording actions or change
endpoint routing. Existing recording requirements and safety notes remain visible.

Web cards expose expandable instructions and references; mobile details expose
numbered instructions and links with an explicit error if opening a reference
fails. Web therapists can copy instructions for either supported exercises or
guide-only exercises into their editable plan fields.

Sources include NHS services, AAOS, Mayo Clinic and ACE, with the relevant URL
attached to each exercise. These references cover technique and activity guidance,
not validation of Movena's scores or screening metrics. A source may describe an
assisted, supported or machine variation; that is not a claim that the video
analyzer reliably assesses every variation. Balance and gait instructions retain
prescribed assistance; users should never remove support to satisfy a camera check.

## Additional guides

The catalog retains the 12 existing analyzer-backed exercises. Four former
placeholders (heel raise, lunge, step-up, hip flexion) now provide instructions,
precautions and therapist-directed dosage guidance. Five additional guides cover
ankle pumps, heel slides, quadriceps sets, straight-leg raises and glute bridges.
Hip flexion is explicitly a seated march; lunge is a supported static variation.

`backend/app/exercises/care_guides.json` is the shared source for the metadata API
and the web fallback catalog. English and Arabic content are included. Mobile
loads guides from the API. `supported_in_app` retains its existing meaning of
analyzer availability; `guidance_available` adds a distinct capability. Guides
have no analysis endpoint, model, automated scores, or recognition claims.

Therapists can select guides in web plans and explicitly copy their instructions
and precautions into editable fields. Existing dosage fields remain clinician
decisions, not validated recommendations for an individual. Patients can read
guides and use the existing prescribed-plan check-in workflow. This change does
not prescribe exercises automatically, change any patient's plan, or add native
mobile prescribing. Video and analysis requirements are disabled for guides in
the web plan editor because the current patient upload flow requires an analyzer.

Content is educational, source-informed material, not a claim of review by a
licensed physical therapist. Local clinical review is still required before
treating it as an approved protocol, particularly after surgery or for people
requiring assistance to stand. No universal numerical dosage or progressions are
assigned. Source links accompany the guides; text is paraphrased, and source
illustrations are not copied.

Sources consulted:

- NHS strength exercises: https://www.nhs.uk/live-well/exercise/strength-exercises/
- NHS sitting exercises: https://www.nhs.uk/live-well/exercise/sitting-exercises/
- NHS knee exercises: https://www.nhs.uk/live-well/exercise/knee-exercises-for-runners/
- AAOS knee exercises: https://www.orthoinfo.org/staying-healthy/knee-exercises?webid=2FDEE455
- AAOS knee conditioning: https://www.orthoinfo.org/recovery/knee-conditioning-program/
- AAOS knee replacement guide: https://www.orthoinfo.org/recovery/total-knee-replacement-exercise-guide/
- South Tees bridge guide: https://www.southtees.nhs.uk/resources/shoulder-bridge/

New analyzers need exercise-specific recording protocols, validity gates, phase
logic, invalid-input coverage, and real-video validation. These guides do not
satisfy those gates and must not be relabelled as analyzer-supported.
