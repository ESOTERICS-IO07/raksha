from app.services.risk.schemas import RiskLevel
from app.services.risk.service import RiskService


def test_risk_weighting():
    service = RiskService()

    result = service.calculate(
        behavior_score=100,
        recipient_score=100,
        intent_score=100,
    )

    assert result.score == 100
    assert result.level == RiskLevel.CRITICAL
    assert result.action_recommendation == "HOLD"


def test_low_risk():
    service = RiskService()

    result = service.calculate(
        behavior_score=10,
        recipient_score=10,
        intent_score=10,
    )

    assert result.level == RiskLevel.LOW
    assert result.action_recommendation == "ALLOW"


def test_critical_bank_impersonation():
    service = RiskService()

    result = service.calculate(
        behavior_score=40,
        recipient_score=80,
        intent_score=94,
        intent_category="BANK_IMPERSONATION",
        amount=50000,
    )

    assert result.score >= 81
    assert result.level == RiskLevel.CRITICAL
    assert result.action_recommendation == "HOLD"