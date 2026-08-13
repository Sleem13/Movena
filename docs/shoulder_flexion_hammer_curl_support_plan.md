# Shoulder Flexion and Hammer Curl Support Plan

Status: Very important implementation task completed as a conservative MVP.

## Scope

- Add a rule-based shoulder-flexion analyzer for visible lowered-raised-lowered forward arm raises.
- Add hammer curl support by reusing the validated curl state machine for visible elbow flexion while keeping grip-orientation limitations explicit.
- Expose both exercises in backend metadata, registry, upload endpoints, frontend exercise library, upload guidance, result cards, and tests.

## Biomechanics and Data Notes

- Shoulder-flexion range references vary by population and measurement method. CDC joint range-of-motion material lists shoulder flexion reference values near full overhead range, and a large general-population shoulder ROM study reports active flexion means around the 150-160 degree range with age effects.
- The analyzer does not use those values as clinical pass/fail cutoffs. It uses adjustable engineering thresholds to detect a visible forward arm raise cycle and score observed range, control, consistency, visibility, and completion.
- The KIMORE rehabilitation dataset, UCO Physical Rehabilitation dataset, DynTherapy MediaPipe-keypoint dataset, and recent upper-limb rehabilitation video datasets show that upper-limb rehabilitation movements are represented in public research data, but they do not clinically validate this product analyzer.
- Hammer curl is grip-specific, but the upload analyzer receives 2D body-pose landmarks, not reliable hand-pose evidence. The MVP therefore analyzes elbow flexion mechanics and reports that neutral grip cannot be confirmed from body pose alone.

## User Safety Boundaries

- No diagnosis, treatment selection, safe-load assessment, pain inference, strength inference, tissue-status inference, or fall-risk inference.
- Stop-use guidance remains shown for pain, dizziness, numbness, unusual symptoms, or imbalance.
- AI feedback supports exercise monitoring and does not replace physiotherapist assessment.

## References Used

- CDC Archive: Normal joint range of motion study material, https://archive.cdc.gov/www_cdc_gov/ncbddd/jointrom/index.html
- BMC Musculoskeletal Disorders: Shoulder range of movement in the general population, https://link.springer.com/article/10.1186/s12891-020-03665-9
- KIMORE rehabilitation movement dataset, https://pubmed.ncbi.nlm.nih.gov/31217121/
- UCO Physical Rehabilitation dataset, https://www.mdpi.com/1424-8220/23/21/8862
- DynTherapy MediaPipe-keypoint dataset, https://data.mendeley.com/datasets/hghdm99rwg
- Upper-limb stroke rehabilitation video dataset, https://www.sciencedirect.com/science/article/pii/S2352340926003719
