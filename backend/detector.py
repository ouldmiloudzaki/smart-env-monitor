"""AI anomaly detector.

Uses an Isolation Forest (unsupervised ML) trained on synthetic "normal"
sensor data. At inference time each incoming reading is scored; points that sit
far from the learned normal region are flagged as anomalies. This is the same
family of model used for real predictive-maintenance / IoT monitoring systems.
"""

from __future__ import annotations

import numpy as np
from sklearn.ensemble import IsolationForest

from simulator import BASE_TEMP, BASE_HUMIDITY, BASE_AQI


class AnomalyDetector:
    def __init__(self, random_state: int = 42) -> None:
        self.model = IsolationForest(
            n_estimators=120,
            contamination=0.05,
            random_state=random_state,
        )
        self._fitted = False

    def train(self, n_samples: int = 2000) -> None:
        """Fit the model on a cloud of normal-condition samples."""
        rng = np.random.default_rng(0)
        temp = rng.normal(BASE_TEMP, 1.2, n_samples)
        humidity = rng.normal(BASE_HUMIDITY, 4.0, n_samples)
        aqi = rng.normal(BASE_AQI, 5.0, n_samples)
        X = np.column_stack([temp, humidity, aqi])
        self.model.fit(X)
        self._fitted = True

    def score(self, temperature: float, humidity: float, aqi: float) -> tuple[bool, float]:
        """Return (is_anomaly, confidence) for a single reading.

        `confidence` is a 0..1 value derived from the model's decision score:
        higher means more confident the point is anomalous.
        """
        if not self._fitted:
            raise RuntimeError("Detector must be trained before scoring.")

        X = np.array([[temperature, humidity, aqi]])
        is_anomaly = bool(self.model.predict(X)[0] == -1)
        # decision_function: positive = normal, negative = anomalous.
        raw = float(self.model.decision_function(X)[0])
        confidence = round(min(1.0, max(0.0, -raw + 0.5)), 3)
        return is_anomaly, confidence
