# Zenodo Static Posture Manual Visual Review

## Reviewed evidence

The review covers the 18 highest-confidence errors selected reproducibly across all three
observed confusion pairs. See `zenodo_posture_visual_review_manifest.csv` and
`zenodo_posture_error_contact_sheet.jpg`.

## Observations

- The 18 rows visually collapse into roughly three recurring subject/scene clusters. Adjacent
  images are frames or near-adjacent poses from the same recording setup, so they must not be
  interpreted as 18 independent failures.
- All reviewed images have usable side-view framing and visible lower-body geometry. Gross
  capture failure does not explain these errors.
- The `bad_back -> good` examples are six closely related outdoor frames of the same subject.
  The back-label boundary is visually subtle and the model's static joint-angle features cannot
  recover the source annotator's intent reliably.
- The `good -> bad_heel` examples use the same outdoor subject/setup. Heel or foot loading is not
  reliably verifiable from a single RGB frame; no force, pressure, pain, or joint-loading claim
  can be supported.
- The `bad_back -> bad_heel` examples are dominated by two indoor recording clusters. Several
  show both trunk lean and visible foot geometry, making a single mutually exclusive source label
  potentially ambiguous.
- Pose-detection misses are concentrated in `bad_back`: 35 of the dataset's 36 missed images.
  This introduces label-dependent selection before classifier training.

## Correlation and leakage boundary

SHA-256 auditing found no exact duplicates across train and test. A coarse 64-bit difference-hash
check found no same-label cross-split pair within Hamming distance 10. These checks reduce the
risk of literal or extremely close duplicate leakage but do not establish participant or sequence
independence. The dataset exposes neither participant IDs nor recording-sequence IDs.

## Decision

Do not tune thresholds or labels using these source-test examples. Use the findings to define a
new development dataset with participant and sequence identifiers, multi-label issue annotation,
and explicit reviewer guidance. The current model remains offline and research-only.
