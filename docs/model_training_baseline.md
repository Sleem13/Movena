# Model Training Baseline

## Feature Preparation

Frame rows are joined to curated labels by normalized `video_path` and aggregated once per video. For left/right knee, left/right hip, and trunk angle, the pipeline calculates mean, population standard deviation, minimum, maximum, range, median, first quartile, and third quartile. Derived features are mean knee asymmetry, mean hip asymmetry, global minimum knee angle, maximum trunk angle, and `180 - min_knee_angle` as an estimated depth proxy. The trunk range is already present in the standard statistics, producing 45 unique ordered numeric features.

Unlabeled videos are excluded. `holdout_test` rows remain protected; other curated rows form the development set. `train_like_reference` is only a historical rule-validation name and does not imply clinical or production training suitability.

## Model Choices

- Logistic Regression provides a scaled linear reference.
- Random Forest provides a small nonlinear tree ensemble and rough interaction capacity.
- RBF SVC provides a scaled margin-based nonlinear reference with probability output.

Every pipeline uses median imputation; scale-sensitive models also use `StandardScaler`. Fixed random states and ordered feature/label contracts support reproducibility. Deep learning is postponed because 16 labeled videos cannot justify a high-capacity temporal or vision model.

## Split Integrity and Reproducibility

The development set has 13 videos and the holdout has three. The minimum development class count is one, so stratified cross-validation is statistically invalid and deliberately skipped. Run preparation, training, evaluation, then prediction in that order. Package versions are pinned in `requirements-dev.txt`.

The generated joblib artifact is trusted local code/data and must never be loaded from an untrusted upload.
