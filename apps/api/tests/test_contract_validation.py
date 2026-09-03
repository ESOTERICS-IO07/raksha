import pytest
from pydantic import ValidationError

from app.services.intent.schemas import IntentCategory, IntentResult
from app.services.intent.providers import LLMProvider, MockIntentProvider
from app.services.risk.schemas import RiskAssessment, RiskLevel
from app.services.risk.service import RiskService
from app.services.friction.schemas import FrictionAction, FrictionDecision
from app.services.friction.service import FrictionService


def test_llm_provider_fallback_to_mock():
    provider = LLMProvider(api_key=None)

    result = provider.classify(
        "Bank officer said my account will be blocked unless I transfer this immediately."
    )

    assert result.provider == "mock"
    assert result.category == IntentCategory.BANK_IMPERSONATION
    assert result.score >= 81


def test_mock_provider_contract():
    provider = MockIntentProvider()

    result = provider.classify("grocery purchase")

    assert isinstance(result, IntentResult)
    assert 0 <= result.score <= 100
    assert result.provider == "mock"
    assert result.model_version == "intent-v1"


def test_intent_schema_rejects_invalid_score():
    with pytest.raises(ValidationError):
        IntentResult(
            category=IntentCategory.NORMAL,
            score=101,
            signals=[],
            attributes={},
            provider="mock",
            model_version="intent-v1",
        )


def test_risk_schema_rejects_invalid_score():
    with pytest.raises(ValidationError):
        RiskAssessment(
            score=101,
            level=RiskLevel.CRITICAL,
            signals=[],
            action_recommendation="HOLD",
        )


def test_risk_schema_accepts_valid_result():
    result = RiskAssessment(
        score=85,
        level=RiskLevel.CRITICAL,
        signals=["HIGH_RISK"],
        action_recommendation="HOLD",
    )

    assert result.score == 85
    assert result.level == RiskLevel.CRITICAL
    assert result.action_recommendation == "HOLD"


def test_friction_schema_contract():
    result = FrictionDecision(
        action=FrictionAction.HOLD,
        title="Payment Paused",
        message="This payment may involve a scam.",
    )

    assert result.action == FrictionAction.HOLD
    assert result.title
    assert result.message


def test_friction_unknown_level_falls_back_to_hold():
    result = FrictionService().decide("UNKNOWN")

    assert result.action == FrictionAction.HOLD


def test_risk_service_output_is_valid_schema():
    result = RiskService().calculate(
        behavior_score=40,
        recipient_score=80,
        intent_score=94,
        intent_category="BANK_IMPERSONATION",
        amount=50000,
    )

    assert isinstance(result, RiskAssessment)
    assert 0 <= result.score <= 100
    assert result.level == RiskLevel.CRITICAL
    assert result.action_recommendation == "HOLD"