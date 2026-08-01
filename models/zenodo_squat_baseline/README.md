# Zenodo Static Squat Posture Baseline

This model is an experimental, image-only research baseline. It uses nine interpretable
MediaPipe angle and heel/foot proxy features to classify the Zenodo source labels `good`,
`bad_back`, and `bad_heel`.

The first reproducible run detected poses in 3,770 of 3,806 images (99.1%). The publisher's
train/test folders were preserved, and SHA-256 auditing found no exact duplicates across the
splits. The initial uncalibrated logistic-regression candidate reached 0.887 accuracy and 0.886
macro F1 on the 956-image source test split. Version 2 reserves a deterministic, stratified 20%
of the source training data for temperature probability calibration. The source test set remains
excluded from model fitting and calibration.

The temperature-scaled experiment improved its calibration slice but worsened probability
quality on the untouched source test set. It is therefore retained only as an audit artifact;
the uncalibrated logistic-regression model remains the default offline research candidate.

These metrics are research evidence only. The dataset does not expose participant identifiers,
so the test split is not proven participant-independent. Static images also cannot evaluate
repetitions, phases, tempo, or temporal movement quality. The artifact is not loaded by the
backend, and promotion remains blocked.

Reproduce the workflow from the repository root:

```powershell
python scripts/prepare_zenodo_squat_dataset.py
python scripts/extract_landmarks_from_images.py
python scripts/create_image_angle_features.py
python scripts/train_zenodo_squat_baseline.py
python scripts/analyze_zenodo_model_errors.py
python scripts/analyze_zenodo_distribution_shift.py
```

Run offline inference for one prepared image with:

```powershell
python scripts/predict_zenodo_squat_baseline.py --image-path "data\\raw\\zenodo_squat_dataset\\test\\Good\\Good (1).jpg"
```
