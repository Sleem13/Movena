# Label Mapping Review Protocol

Every raw folder name or exercise code is recorded in `exercise_label_mapping.csv`. Reviewers must verify source documentation, protocol meaning, exercise identity, issue-label meaning, modality, and whether the label is descriptive rather than diagnostic.

## Workflow

1. Keep new or coded labels at low confidence with `requires_review=true`.
2. Record the raw folder/code exactly; do not rewrite source provenance.
3. Map only to an existing taxonomy ID supported by documentation.
4. Use `needs_more_info` when the codebook or protocol is unavailable.
5. Use `approved` only after a named reviewer verifies the mapping; record `reviewed_by`.
6. Use `rejected` when a proposed mapping is unsupported.
7. Re-export metadata after approval; do not manually patch derived training tables.

Low- and medium-confidence mappings are not training-ready. Labels must not be converted into diagnoses or claims about pain, pathology, fall risk, or treatment suitability.

