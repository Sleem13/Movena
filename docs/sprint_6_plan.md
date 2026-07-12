# Sprint 6 Plan

## Theme

Experimental ML Integration and Custom Video Augmentation.

## Goal

Expose the trusted Sprint 5 baseline as an optional, non-blocking second opinion while adding a conservative, auditable video augmentation workflow for robustness experiments.

## Scope

- `include_ml=true` optional inference after rule-based analysis.
- Exact 46-feature adaptation from detected pose frames.
- Graceful disabled ML response when artifacts or features are unavailable.
- OpenCV augmentation helper, metadata validation, notebook, dataset folders, and tests.
- Documentation that separates synthetic robustness data from independent evidence.

## Non-goals

No deep learning, ML override of rule feedback, clinical claims, automatic diagnosis, new exercises, label-changing joint warps, authentication, or complex storage.

## Acceptance Criteria

- Default endpoint behavior remains rule-based and unchanged.
- Optional ML output always carries an experimental or unavailable warning.
- Missing/corrupt artifacts cannot fail the endpoint.
- Augmentations never overwrite source files and retain labels by default.
- Augmented videos are outside raw data and ignored by Git.
- Notebook, registry validator, structure checker, docs, and all tests pass.

## Risks

The 16-video model is underpowered and imbalanced. Online features must remain byte-for-byte compatible in name/order with training. Augmented clips are correlated with their sources and can leak across splits. Horizontal flip changes left/right semantics. Codec conversion may alter image quality. Every output needs visual and physiotherapist review before experimental training use.
