# Dataset Registry Design

The registry is generated from structural audit evidence rather than dataset-name assumptions. It records source path, status, modality, file counts, annotation candidates, preliminary exercise scope, compatibility, adapter need, priority, and limitations.

## Status Semantics

- `compatible_candidate`: contains an explicitly supported video modality and known current path.
- `adapter_required`: data exists but its modality, labels, or schema are not accepted by the current squat video pipeline.
- `missing_or_incomplete`: folder is absent or contains no meaningful files beyond placeholders.

`usable_for_current_squat_mvp=true` is deliberately narrow. A high-priority name alone is insufficient; usable video files or a separately reviewed compatible feature/label contract are required. `squat_kaggle` remains adapter-required because its numeric label semantics and provenance require review. Zenodo remains image-only and is not temporal squat-video evidence.

The audit and registry are local structural metadata. They do not establish license clearance, participant consent, label equivalence, scientific validity, or clinical validity.

