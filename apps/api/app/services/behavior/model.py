"""Isolation Forest Anomaly Detection Model.

Uses scikit-learn's IsolationForest with random_state=42 to detect multidimensional
anomalies in customer transaction features, calibrated to a 0–100 anomaly scale.
"""

from __future__ import annotations

from typing import Optional
import numpy as np
from sklearn.ensemble import IsolationForest

from .schemas import BehaviorFeatures


class BehaviorAnomalyModel:
    """Isolation Forest based anomaly detector for behavioral feature vectors."""

    _instance: Optional["BehaviorAnomalyModel"] = None

    def __init__(self, random_state: int = 42, n_estimators: int = 100) -> None:
        self.random_state = random_state
        self.n_estimators = n_estimators
        self.model = IsolationForest(
            n_estimators=self.n_estimators,
            contamination=0.05,
            random_state=self.random_state,
        )
        self._is_fitted = False
        self._train_default_baseline()

    def _train_default_baseline(self) -> None:
        """Fit IsolationForest on a deterministic synthetic distribution of normal transactions.

        Features vector definition:
        [amount_deviation, amount_to_avg_ratio, hour_deviation, is_new_recipient, is_new_device, is_new_location, velocity_1h, velocity_24h]
        """
        rng = np.random.RandomState(self.random_state)
        n_samples = 300

        # Normal transaction distribution
        amt_dev = rng.exponential(scale=0.4, size=n_samples)  # most deviations near 0
        amt_ratio = rng.normal(loc=1.0, scale=0.3, size=n_samples)
        amt_ratio = np.clip(amt_ratio, 0.2, 2.5)
        hour_dev = np.zeros(n_samples)  # normal hours
        is_new_rcp = rng.binomial(n=1, p=0.08, size=n_samples)
        is_new_dev = rng.binomial(n=1, p=0.02, size=n_samples)
        is_new_loc = rng.binomial(n=1, p=0.02, size=n_samples)
        vel_1h = rng.poisson(lam=0.2, size=n_samples)
        vel_24h = rng.poisson(lam=1.5, size=n_samples)

        X_train = np.column_stack(
            [
                amt_dev,
                amt_ratio,
                hour_dev,
                is_new_rcp,
                is_new_dev,
                is_new_loc,
                vel_1h,
                vel_24h,
            ]
        )

        self.model.fit(X_train)
        self._is_fitted = True

    def predict_anomaly_score(self, feature_vector: np.ndarray) -> tuple[int, float]:
        """Compute the Isolation Forest anomaly score for an input feature vector.

        Returns:
            tuple: (calibrated_score_0_to_100: int, raw_decision_function_score: float)
        """
        if not self._is_fitted:
            self._train_default_baseline()

        # decision_function returns positive for inliers (~ 0.1 to 0.2), negative for outliers (~ -0.1 to -0.35)
        raw_df = float(self.model.decision_function(feature_vector)[0])

        # Calibration mapping:
        # df >= 0.12  -> 0 (completely normal)
        # df == 0.00  -> ~35
        # df == -0.15 -> ~75
        # df <= -0.28 -> 100 (extreme anomaly)
        upper_bound = 0.12
        lower_bound = -0.28

        normalized = (upper_bound - raw_df) / (upper_bound - lower_bound)
        calibrated_score = int(np.clip(round(normalized * 100), 0, 100))

        return calibrated_score, raw_df

    @classmethod
    def get_shared_model(cls) -> "BehaviorAnomalyModel":
        """Singleton accessor for the pre-trained Isolation Forest model."""
        if cls._instance is None:
            cls._instance = cls(random_state=42)
        return cls._instance
