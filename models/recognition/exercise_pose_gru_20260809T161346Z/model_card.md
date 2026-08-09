# Temporal Exercise Classifier — Development Candidate

This bidirectional GRU uses complete pose sequences resampled to a fixed duration. Training, validation, and holdout videos are disjoint and stratified by exercise. Participant identities are unavailable, so unseen-person and clinical performance are not established. Validation-set temperature scaling calibrates confidence, and an evidence-derived threshold returns an uncertain result below the accepted range. Predictions above the threshold still require manual confirmation and do not provide movement-quality feedback.
