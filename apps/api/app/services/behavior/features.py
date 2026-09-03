"""Transaction Feature Extraction.

Extracts normalized numerical and categorical features by comparing a TransactionContext
against a CustomerBehaviorProfile.
"""

from __future__ import annotations

from datetime import datetime
from typing import Any, Optional, Sequence, Union
import numpy as np

from .baseline import BehaviorBaselineCalculator
from .schemas import (
    BehaviorFeatures,
    CustomerBehaviorProfile,
    LocationContext,
    TransactionContext,
)


class BehaviorFeatureExtractor:
    """Extracts behavioral risk features from transaction context and customer baseline."""

    @classmethod
    def _extract_hour(cls, timestamp: Optional[Union[datetime, str]]) -> int:
        """Extract hour of day (0-23) from timestamp, defaulting to 12 (midday) if missing."""
        dt = BehaviorBaselineCalculator.parse_datetime(timestamp)
        if dt is not None:
            return dt.hour
        return 12

    @classmethod
    def _calculate_hour_deviation(cls, tx_hour: int, usual_hours: Sequence[int]) -> float:
        """Calculate circular hour distance from the customer's usual transacting hours.

        Circular distance accounts for midnight wrap-around:
        e.g., distance between 23 (11pm) and 1 (1am) is 2 hours, not 22 hours.
        """
        if not usual_hours:
            # Fallback to standard daytime hours [8..22]
            usual_hours = BehaviorBaselineCalculator.DEFAULT_USUAL_HOURS

        min_distance = 24.0
        for h in usual_hours:
            diff = abs(tx_hour - int(h))
            circ_dist = min(diff, 24 - diff)
            if circ_dist < min_distance:
                min_distance = float(circ_dist)
                if min_distance == 0.0:
                    break
        return float(min_distance)

    @classmethod
    def _extract_recipient_frequency(
        cls,
        recipient_id: str,
        profile: CustomerBehaviorProfile,
    ) -> int:
        """Determine historical count of transactions to the specified recipient."""
        if not recipient_id:
            return 0

        # If historical transactions are provided, count exact matches
        if profile.historical_transactions:
            count = sum(
                1
                for tx in profile.historical_transactions
                if isinstance(tx, dict) and tx.get("recipient_id") == recipient_id
            )
            return count

        # If frequent_recipients list is present
        if recipient_id in profile.frequent_recipients:
            # Higher ranking in frequent list implies higher frequency
            try:
                idx = profile.frequent_recipients.index(recipient_id)
                return max(1, len(profile.frequent_recipients) - idx)
            except ValueError:
                return 1

        return 0

    @classmethod
    def _check_new_device(
        cls,
        device_id: Optional[str],
        known_devices: Sequence[str],
    ) -> bool:
        """Check if device is unfamiliar to the customer."""
        if not device_id:
            return False
        if not known_devices:
            # First transaction with unknown device list is not considered anomalous by default
            return False
        return device_id not in known_devices

    @classmethod
    def _check_new_location(
        cls,
        location: Optional[Union[LocationContext, dict[str, Any], str]],
        known_locations: Sequence[str],
    ) -> bool:
        """Check if transaction location is unfamiliar to the customer."""
        if not location or not known_locations:
            return False

        loc_str = ""
        if isinstance(location, LocationContext):
            loc_str = location.region or location.country or ""
        elif isinstance(location, dict):
            loc_str = str(location.get("region") or location.get("country") or "")
        elif isinstance(location, str):
            loc_str = location

        if not loc_str:
            return False

        return loc_str not in known_locations

    @classmethod
    def extract_features(
        cls,
        context: Union[TransactionContext, dict[str, Any]],
        profile: Union[CustomerBehaviorProfile, dict[str, Any]],
    ) -> BehaviorFeatures:
        """Extract comprehensive behavioral features."""
        # Normalize inputs to Pydantic models
        if isinstance(context, dict):
            context = TransactionContext(**context)
        if isinstance(profile, dict):
            profile = CustomerBehaviorProfile(**profile)

        amount = float(context.amount)
        avg_amt = float(profile.avg_amount) if profile.avg_amount > 0 else BehaviorBaselineCalculator.DEFAULT_AVG_AMOUNT
        std_amt = float(profile.std_amount) if profile.std_amount > 0 else max(avg_amt * 0.3, 100.0)

        # 1. Amount Deviation (Z-score)
        # Cap minimum deviation to 0 if amount is within normal bounds
        raw_deviation = (amount - avg_amt) / max(std_amt, 10.0)
        amount_deviation = max(0.0, raw_deviation)

        # 2. Amount to Average Ratio
        amount_to_avg_ratio = amount / max(avg_amt, 1.0)

        # 3. Hour Deviation
        tx_hour = cls._extract_hour(context.timestamp)
        hour_deviation = cls._calculate_hour_deviation(tx_hour, profile.usual_hours)

        # 4. Recipient Familiarity
        recipient_freq = cls._extract_recipient_frequency(context.recipient_id, profile)
        is_new_recipient = recipient_freq == 0

        # 5. Device Novelty
        is_new_device = cls._check_new_device(context.device_id, profile.known_devices)

        # 6. Location Novelty
        is_new_location = cls._check_new_location(context.location, profile.known_locations)

        # 7. Velocity metrics
        v1h = int(profile.recent_transaction_count_1h)
        v24h = int(profile.recent_transaction_count_24h)

        return BehaviorFeatures(
            amount_deviation=amount_deviation,
            amount_to_avg_ratio=amount_to_avg_ratio,
            hour_deviation=hour_deviation,
            recipient_frequency=recipient_freq,
            is_new_recipient=is_new_recipient,
            is_new_device=is_new_device,
            is_new_location=is_new_location,
            velocity_1h=v1h,
            velocity_24h=v24h,
            isolation_forest_anomaly_score=0.0,
        )

    @classmethod
    def features_to_vector(cls, features: BehaviorFeatures) -> np.ndarray:
        """Convert BehaviorFeatures to numeric feature vector for IsolationForest inference."""
        return np.array(
            [
                features.amount_deviation,
                features.amount_to_avg_ratio,
                features.hour_deviation,
                1.0 if features.is_new_recipient else 0.0,
                1.0 if features.is_new_device else 0.0,
                1.0 if features.is_new_location else 0.0,
                float(features.velocity_1h),
                float(features.velocity_24h),
            ],
            dtype=np.float64,
        ).reshape(1, -1)

