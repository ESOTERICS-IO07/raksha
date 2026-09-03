from typing import Protocol

from .schemas import IntentCategory, IntentResult


class IntentProvider(Protocol):
    def classify(self, reason: str) -> IntentResult:
        ...


class MockIntentProvider:
    """
    Deterministic provider for the hackathon demo.
    No external LLM is required.
    """

    def classify(self, reason: str) -> IntentResult:
        text = (reason or "").lower()

        if any(
            phrase in text
            for phrase in [
                "bank officer",
                "bank employee",
                "account will be blocked",
                "account blocked",
                "verify my account",
            ]
        ):
            return IntentResult(
                category=IntentCategory.BANK_IMPERSONATION,
                score=94,
                signals=[
                    "AUTHORITY_IMPERSONATION",
                    "ACCOUNT_BLOCK_THREAT",
                    "URGENT_TRANSFER",
                ],
                attributes={
                    "urgency": 0.94,
                    "authority_impersonation": 0.97,
                    "coercion": 0.82,
                },
                provider="mock",
                model_version="intent-v1",
            )

        if any(
            word in text
            for word in ["otp", "one time password", "one-time password"]
        ):
            return IntentResult(
                category=IntentCategory.OTP_SCAM,
                score=95,
                signals=["OTP_REQUEST", "URGENT_TRANSFER"],
                attributes={
                    "urgency": 0.90,
                    "coercion": 0.85,
                },
                provider="mock",
                model_version="intent-v1",
            )

        if any(
            word in text
            for word in ["investment", "guaranteed return", "double your money"]
        ):
            return IntentResult(
                category=IntentCategory.INVESTMENT_SCAM,
                score=88,
                signals=["INVESTMENT_PROMISE", "HIGH_RETURN_CLAIM"],
                attributes={
                    "urgency": 0.70,
                    "coercion": 0.50,
                },
                provider="mock",
                model_version="intent-v1",
            )

        if any(
            word in text
            for word in ["refund", "refund fee", "refund charge"]
        ):
            return IntentResult(
                category=IntentCategory.REFUND_SCAM,
                score=82,
                signals=["REFUND_REQUEST", "PAYMENT_DEMAND"],
                attributes={
                    "urgency": 0.65,
                    "coercion": 0.55,
                },
                provider="mock",
                model_version="intent-v1",
            )

        return IntentResult(
            category=IntentCategory.NORMAL,
            score=10,
            signals=[],
            attributes={
                "urgency": 0.0,
                "authority_impersonation": 0.0,
                "coercion": 0.0,
            },
            provider="mock",
            model_version="intent-v1",
        )


class LLMProvider:
    """
    Placeholder for future LLM integration.

    The hackathon demo uses MockIntentProvider so the system
    remains deterministic and works without an API key.
    """

    def __init__(self, api_key: str | None = None):
        self.api_key = api_key

    def classify(self, reason: str) -> IntentResult:
        # Safe fallback for demo.
        return MockIntentProvider().classify(reason)