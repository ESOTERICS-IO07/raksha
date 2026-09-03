"""Shared API Contract Layer."""

from .dashboard import DashboardCluster, DashboardSummary, DashboardTransaction
from .errors import ErrorDetail, ErrorResponse
from .friction import FrictionAction, FrictionDecision
from .intent import IntentCategory, IntentResult
from .recipient import RecipientNetwork, RecipientProfile, RecipientResult
from .risk import ActionRecommendation, RiskAssessment, RiskLevel
from .scenario import ScenarioResponse, ScenarioRunResponse

from .transaction import TransactionContext, LocationContext
from .behavior import BehaviorResult, CustomerBehaviorProfile, BehaviorFeatures

__all__ = [
    "DashboardCluster",
    "DashboardSummary",
    "DashboardTransaction",
    "ErrorDetail",
    "ErrorResponse",
    "FrictionAction",
    "FrictionDecision",
    "IntentCategory",
    "IntentResult",
    "RecipientNetwork",
    "RecipientProfile",
    "RecipientResult",
    "ActionRecommendation",
    "RiskAssessment",
    "RiskLevel",
    "ScenarioResponse",
    "ScenarioRunResponse",
    "TransactionContext",
    "LocationContext",
    "BehaviorResult",
    "CustomerBehaviorProfile",
    "BehaviorFeatures",
]
