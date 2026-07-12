# Sprint 6 Validation Checklist

- [x] Optional ML service and exact feature adapter exist.
- [x] Default endpoint omits ML output.
- [x] `include_ml=true` returns enabled or safely disabled output.
- [x] Rule-based result survives ML failure.
- [x] Experimental/non-clinical warning is present.
- [x] Augmentation helper never overwrites source videos.
- [x] Mild transforms preserve dimensions.
- [x] Metadata schema and missing-source validation are tested.
- [x] Augmented folder structure is managed by the structure checker.
- [x] Augmented videos are ignored by Git while `.gitkeep` files remain tracked.
- [x] Notebook contains strategy, generation, QA, validation, and limitation sections.
- [ ] Real augmentations generated and visually reviewed; intentionally pending user-controlled notebook execution.
- [ ] Augmented labels reviewed by a licensed physiotherapist.
- [ ] More independent real videos collected.
