"""Mock interfaces for Person 4's unfinished Intent + Risk + Friction components.

These are EXPLICITLY named Mock* and exist ONLY to allow the platform API
boundary to be tested before Person 4 merges their implementation.

Rules:
- Do not use these in production logic.
- Do not hard-code real fraud decisions here.
- Replace by importing from app.services.intent/risk/friction after P4 merges.
"""

from __future__ import annotations

from typing import Any

from app.schemas.intent import IntentResult, IntentCategory
from app.schemas.risk import RiskAssessment, RiskLevel, ActionRecommendation
from app.schemas.friction import FrictionDecision, FrictionAction


def MockIntentProvider(tx_context: Any) -> dict[str, Any]:
    """Stub for Person 4's Intent Engine. Returns a neutral UNKNOWN result."""
    return IntentResult(
        category=IntentCategory.UNKNOWN,
        score=0,
        signals=[],
        attributes={},
        provider="mock",
        model_version="intent-v1",
    ).model_dump()


def MockRiskService(
    behavior: dict[str, Any],
    recipient: dict[str, Any],
    intent: dict[str, Any],
) -> dict[str, Any]:
    """Stub for Person 4's Risk Engine. Returns a neutral LOW result.

    Frozen weights (Person 4 will implement):
        behavior  35%
        recipient 25%
        intent    40%
    """
    return RiskAssessment(
        score=0,
        level=RiskLevel.LOW,
        signals=[],
        action_recommendation=ActionRecommendation.ALLOW,
        engine_version="risk-v1",
    ).model_dump()


def MockFrictionService(risk: dict[str, Any]) -> dict[str, Any]:
    """Stub for Person 4's Adaptive Friction Engine. Returns ALLOW."""
    return FrictionDecision(
        action=FrictionAction.ALLOW,
        title="Processing",
        message="Transaction is being evaluated.",
    ).model_dump()
