"""Behavior Intelligence Engine Package.

Provides customer-specific behavioral anomaly detection conforming to CONTRACTS.md.
"""

from .baseline import BehaviorBaselineCalculator
from .engine import BehaviorEngine, analyze_behavior
from .features import BehaviorFeatureExtractor
from .model import BehaviorAnomalyModel
from .rules import BehaviorRuleEngine
from .schemas import (
    BehaviorFeatures,
    BehaviorResult,
    BehaviorSignal,
    CustomerBehaviorProfile,
    LocationContext,
    TransactionContext,
)

__all__ = [
    "BehaviorEngine",
    "analyze_behavior",
    "BehaviorBaselineCalculator",
    "BehaviorFeatureExtractor",
    "BehaviorAnomalyModel",
    "BehaviorRuleEngine",
    "BehaviorResult",
    "BehaviorSignal",
    "BehaviorFeatures",
    "CustomerBehaviorProfile",
    "TransactionContext",
    "LocationContext",
]

