"""Behavior Intelligence Engine Main Coordinator.

Orchestrates feature extraction, baseline evaluation, Isolation Forest ML anomaly scoring,
and heuristic behavioral rules to produce a contract-compliant BehaviorResult.

Adheres strictly to CONTRACTS.md Section 10:
Input: TransactionContext + CustomerBehaviorProfile
Output: {
    "score": 0-100 (integer),
    "signals": list[str],
    "features": dict,
    "model_version": "behavior-v1"
}
Must NOT decide ALLOW, VERIFY, STRONG_VERIFY, or HOLD.
"""

from __future__ import annotations

from typing import Any, Optional, Union

from .baseline import BehaviorBaselineCalculator
from .features import BehaviorFeatureExtractor
from .model import BehaviorAnomalyModel
from .rules import BehaviorRuleEngine
from .schemas import (
    BehaviorFeatures,
    BehaviorResult,
    CustomerBehaviorProfile,
    TransactionContext,
)


class BehaviorEngine:
    """Core Behavior Intelligence Engine."""

    def __init__(self, anomaly_model: Optional[BehaviorAnomalyModel] = None) -> None:
        self.anomaly_model = anomaly_model or BehaviorAnomalyModel.get_shared_model()

    def analyze(
        self,
        context: Union[TransactionContext, dict[str, Any]],
        profile: Optional[Union[CustomerBehaviorProfile, dict[str, Any]]] = None,
    ) -> BehaviorResult:
        """Analyze transaction for customer-specific behavioral anomalies.

        Args:
            context: Transaction context (TransactionContext model or dict).
            profile: Customer behavioral profile (CustomerBehaviorProfile model or dict).

        Returns:
            BehaviorResult conforming strictly to the contract.
        """
        # 1. Normalize TransactionContext
        if isinstance(context, dict):
            tx_context = TransactionContext(**context)
        elif isinstance(context, TransactionContext):
            tx_context = context
        else:
            raise ValueError(f"Invalid transaction context type: {type(context)}")

        # 2. Normalize CustomerBehaviorProfile (fallback to cold-start default if absent or empty)
        if profile is None or not profile:
            user_profile = BehaviorBaselineCalculator.get_default_profile(tx_context.user_id)
        elif isinstance(profile, dict):
            profile_data = dict(profile)
            if not profile_data.get("user_id"):
                profile_data["user_id"] = tx_context.user_id
            user_profile = CustomerBehaviorProfile(**profile_data)
        elif isinstance(profile, CustomerBehaviorProfile):
            user_profile = profile
        else:
            user_profile = BehaviorBaselineCalculator.get_default_profile(tx_context.user_id)

        # 3. Extract Features
        features: BehaviorFeatures = BehaviorFeatureExtractor.extract_features(
            tx_context, user_profile
        )

        # 4. ML Anomaly Scoring via Isolation Forest
        feature_vector = BehaviorFeatureExtractor.features_to_vector(features)
        ml_score, raw_decision_score = self.anomaly_model.predict_anomaly_score(feature_vector)
        features.isolation_forest_anomaly_score = raw_decision_score

        # 5. Behavioral Rule Evaluation
        rule_score, signals = BehaviorRuleEngine.evaluate(tx_context, user_profile, features)

        # 6. Score Blending & Calibration
        # Combine ML anomaly score (40%) and Rule score (60%)
        # If no anomalous signals fired and deviation is low, suppress to low baseline
        if not signals and features.amount_deviation < 1.0 and features.hour_deviation < 1.0:
            final_score = int(min(25, round(ml_score * 0.35)))
        else:
            blended = 0.40 * ml_score + 0.60 * rule_score
            # Max-escalation if strong rule signals triggered
            final_score = int(round(max(blended, rule_score * 0.9)))

        # Strictly clamp integer score to [0, 100]
        final_score = max(0, min(100, final_score))

        return BehaviorResult(
            score=final_score,
            signals=signals,
            features=features.to_contract_dict(),
            model_version="behavior-v1",
        )


# Module-level shared instance and convenient functional interface
_default_engine = BehaviorEngine()


def analyze_behavior(
    context: Union[TransactionContext, dict[str, Any]],
    profile: Optional[Union[CustomerBehaviorProfile, dict[str, Any]]] = None,
) -> dict[str, Any]:
    """Functional interface for behavior evaluation returning a contract-compliant dictionary.

    Example:
        result = analyze_behavior(tx_context, user_profile)
        # {
        #   "score": 87,
        #   "signals": ["AMOUNT_ABOVE_NORMAL", "UNUSUAL_TIME", "NEW_BEHAVIOR_PATTERN"],
        #   "features": {"amount_deviation": 4.8, "hour_deviation": 2.1, ...},
        #   "model_version": "behavior-v1"
        # }
    """
    result = _default_engine.analyze(context, profile)
    return result.model_dump()
