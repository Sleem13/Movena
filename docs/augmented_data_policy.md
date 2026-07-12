# Augmented Data Policy

Augmented videos may improve robustness to brightness, contrast, mild camera rotation, compression, and other controlled acquisition variation. They do not add participants, independent sessions, clinical diversity, or clinical validity.

- Keep real and augmented sources explicitly separated with `source_type`, source paths, and transformation parameters.
- Augmented variants must inherit their source split to prevent leakage.
- Report real-only and augmented-inclusive counts and metrics separately whenever augmented data is used.
- Never claim clinical validity or class coverage from synthetic variants.
- Avoid label-changing augmentation. Any intentional label change requires explicit documentation, visual QA, and manual physiotherapist review.
- Do not warp joints, fabricate valgus, distort bodies, apply heavy crops, or use transformations that hide clinically relevant landmarks.
- `safe_for_training=true` is a structural QA flag, not proof that the clip is clinically or scientifically valid.
- Preserve the original recording and never overwrite it.

Real recordings remain the priority for every missing or underrepresented class.
