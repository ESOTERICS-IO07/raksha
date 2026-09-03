from app.services.intent.providers import MockIntentProvider
from app.services.intent.schemas import IntentCategory
from app.services.intent.service import IntentService


def test_bank_impersonation_detection():
    service = IntentService(MockIntentProvider())

    result = service.analyze(
        "Bank officer said my account will be blocked unless I transfer this immediately."
    )

    assert result.category == IntentCategory.BANK_IMPERSONATION
    assert result.score >= 81
    assert "AUTHORITY_IMPERSONATION" in result.signals


def test_normal_reason():
    service = IntentService(MockIntentProvider())

    result = service.analyze("grocery purchase")

    assert result.category == IntentCategory.NORMAL
    assert 0 <= result.score <= 100


def test_empty_reason():
    service = IntentService(MockIntentProvider())

    result = service.analyze("")

    assert 0 <= result.score <= 100