# Dataset Adapter Validation

Validation checks metadata contracts and modality routing; it does not approve labels or training use.

| dataset_name | adapter_name | status | modality | sample_count | checked_sample_count | requires_manual_mapping | errors | warnings |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| custom_videos | CustomVideosAdapter | passed | video | 24 | 5 | False |  |  |
| dyntherapy | DynTherapyAdapter | needs_manual_mapping | skeleton_3d | 1 | 1 | True |  |  |
| kimore | KiMoReAdapter | needs_manual_mapping | skeleton_3d | 1 | 1 | True |  |  |
| Physical-therapy exercises | PhysicalTherapyExercisesAdapter | missing_dataset | unknown | 0 | 0 | True |  |  |
| rehab24_6 | Rehab246Adapter | needs_manual_mapping | mixed | 910 | 5 | True |  |  |
| squat_kaggle | SquatKaggleAdapter | needs_manual_mapping | tabular_features | 1 | 1 | True |  |  |
| uci_physical_therapy_exercises | UCIPhysicalTherapyAdapter | needs_manual_mapping | sensor_timeseries | 200 | 5 | True |  |  |
| uco_physical_rehab | UCOPhysicalRehabAdapter | missing_dataset | missing_or_incomplete | 0 | 0 | True |  |  |
| ui_prmd | UIPRMDAdapter | needs_manual_mapping | skeleton_3d | 3 | 3 | True |  |  |
| zenodo_squat_dataset | ZenodoSquatAdapter | needs_manual_mapping | image | 3806 | 5 | True |  |  |
