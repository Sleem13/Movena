# Sprint 14 — Multi-Dataset ML/DL Expansion Architecture

Sprint 14 establishes modality-aware discovery, taxonomy, unified sample metadata, fail-closed adapters/guards, separate feature tracks, a governed model registry, and CPU-safe ML/DL scaffolds. It does not merge all sources, train deep models, promote a model, or activate new exercises.

The current application supports bodyweight squat, sit-to-stand, knee extension, shoulder abduction, and hip abduction. Rule-based biomechanics remains primary. All ML/DL output remains experimental and non-diagnostic.

## Reproducible dry run

```powershell
python scripts/audit_raw_datasets.py
python scripts/build_dataset_registry.py
python scripts/export_unified_dataset_metadata.py
python scripts/train_ml_track.py --dry-run --track video_pose --exercise bodyweight_squat
python -m pytest
```

The training dry run may report a missing or blocked feature table; that is a safe result, not permission to bypass participant grouping or label requirements.
