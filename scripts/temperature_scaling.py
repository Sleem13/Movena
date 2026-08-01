"""Serializable probability temperature scaling for experimental classifiers."""

from __future__ import annotations

import numpy as np
from scipy.optimize import minimize_scalar
from sklearn.metrics import log_loss


class TemperatureScaledClassifier:
    """Apply development-only temperature scaling to fitted class probabilities."""

    def __init__(self, estimator, temperature: float):
        self.estimator = estimator
        self.temperature = float(temperature)
        self.classes_ = estimator.classes_

    @classmethod
    def fit_from_calibration(cls, estimator, features, labels):
        probabilities = np.clip(estimator.predict_proba(features), 1e-12, 1.0)
        classes = list(estimator.classes_)

        def objective(temperature: float) -> float:
            scaled = cls.scale_probabilities(probabilities, temperature)
            return float(log_loss(labels, scaled, labels=classes))

        optimized = minimize_scalar(objective, bounds=(0.05, 10.0), method="bounded")
        if not optimized.success:
            raise RuntimeError("Temperature calibration optimization did not converge.")
        return cls(estimator, float(optimized.x))

    @staticmethod
    def scale_probabilities(probabilities: np.ndarray, temperature: float) -> np.ndarray:
        logits = np.log(np.clip(probabilities, 1e-12, 1.0)) / float(temperature)
        logits -= logits.max(axis=1, keepdims=True)
        exponentiated = np.exp(logits)
        return exponentiated / exponentiated.sum(axis=1, keepdims=True)

    def predict_proba(self, features) -> np.ndarray:
        return self.scale_probabilities(
            self.estimator.predict_proba(features), self.temperature
        )

    def predict(self, features) -> np.ndarray:
        probabilities = self.predict_proba(features)
        return np.asarray(self.classes_)[probabilities.argmax(axis=1)]
