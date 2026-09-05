"""Behavioral Heuristic Rules Engine.

Evaluates deterministic rule-based checks on behavioral features to produce
standardized machine-readable signals and rule-based risk scores.
"""

from __future__ import annotations

from typing import Any, Sequence, Union

from .schemas import (
    BehaviorFeatures,
    BehaviorSignal,
    CustomerBehaviorProfile,
    TransactionContext,
)


class BehaviorRuleEngine:
    """Evaluates deterministic behavioral fraud rules against transaction context and features."""

    @classmethod
    def evaluate(
        cls,
        context: Union[TransactionContext, dict[str, Any]],
        profile: Union[CustomerBehaviorProfile, dict[str, Any]],
        features: BehaviorFeatures,
    ) -> tuple[int, list[str]]:
        """Evaluate all behavioral rules.

        Returns:
            tuple: (rule_score_0_to_100: int, signals: list[str])
        """
        if isinstance(context, dict):
            context = TransactionContext(**context)
        if isinstance(profile, dict):
            profile = CustomerBehaviorProfile(**profile)

        signals: list[str] = []
        score_components: list[int] = []

        amount = float(context.amount)
        avg_amt = float(profile.avg_amount) if profile.avg_amount > 0 else 1500.0

        # Rule 1: Amount Above Normal (AMOUNT_ABOVE_NORMAL)
        if features.amount_deviation >= 2.0 or features.amount_to_avg_ratio >= 2.5:
            signals.append(BehaviorSignal.AMOUNT_ABOVE_NORMAL.value)
            amt_score = min(60, int(30 + features.amount_deviation * 6))
            score_components.append(amt_score)

        # Rule 2: Extreme Amount Spike (SPIKE_AMOUNT)
        # 10x normal average or large absolute transaction for low-volume user
        if amount >= 10.0 * avg_amt or (avg_amt <= 2000.0 and amount >= 50000.0):
            signals.append(BehaviorSignal.SPIKE_AMOUNT.value)
            score_components.append(70)

        # Rule 3: Unusual Time / Off-Hours (UNUSUAL_TIME)
        # Distance >= 2.0 hours from customer's habitual transaction window
        if features.hour_deviation >= 2.0:
            signals.append(BehaviorSignal.UNUSUAL_TIME.value)
            time_score = min(50, int(25 + features.hour_deviation * 6))
            score_components.append(time_score)

        # Rule 4: High Transaction Velocity (HIGH_TRANSACTION_VELOCITY)
        if features.velocity_1h >= 3:
            signals.append(BehaviorSignal.HIGH_TRANSACTION_VELOCITY.value)
            score_components.append(min(50, 20 + features.velocity_1h * 5))
        elif features.velocity_1h >= 2:
            score_components.append(15)

        # Rule 5: New Device (NEW_DEVICE)
        if features.is_new_device:
            signals.append(BehaviorSignal.NEW_DEVICE.value)
            score_components.append(20)

        # Rule 6: Unusual Location (UNUSUAL_LOCATION)
        if features.is_new_location:
            signals.append(BehaviorSignal.UNUSUAL_LOCATION.value)
            score_components.append(20)

        # Rule 7: New Recipient (UNFAMILIAR_RECIPIENT_FOR_USER)
        if features.is_new_recipient:
            # Soft behavioral indicator for unfamiliar recipient
            score_components.append(10)

        # Rule 8: Compound Novelty / Social Engineering Pattern (NEW_BEHAVIOR_PATTERN)
        # Triggered when multiple anomaly vectors coincide simultaneously:
        # e.g., (amount spike/above normal OR high amount) + (unusual time OR new recipient) + (new device OR high amount)
        is_high_amount = (
            features.amount_deviation >= 2.0
            or features.amount_to_avg_ratio >= 3.0
            or amount >= 25000.0
        )
        is_time_anomaly = features.hour_deviation >= 2.0
        is_novelty = features.is_new_recipient or features.is_new_device

        if is_high_amount and (is_time_anomaly or is_novelty):
            if BehaviorSignal.NEW_BEHAVIOR_PATTERN.value not in signals:
                signals.append(BehaviorSignal.NEW_BEHAVIOR_PATTERN.value)
            score_components.append(45)

        # Calculate combined rule score
        if not score_components:
            rule_score = 0
        else:
            # Combine primary score + damped secondary scores
            sorted_scores = sorted(score_components, reverse=True)
            primary = sorted_scores[0]
            secondary = sum(sorted_scores[1:]) * 0.35
            rule_score = int(min(100, round(primary + secondary)))

        return rule_score, list(dict.fromkeys(signals))
