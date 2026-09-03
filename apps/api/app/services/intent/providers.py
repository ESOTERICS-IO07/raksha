import json
import os
from typing import Protocol

from dotenv import load_dotenv
from openai import OpenAI

from .schemas import IntentCategory, IntentResult

load_dotenv()


class IntentProvider(Protocol):
    def classify(self, reason: str) -> IntentResult:
        ...


class MockIntentProvider:
    def classify(self, reason: str) -> IntentResult:
        text = (reason or "").lower()

        if any(phrase in text for phrase in [
            "bank officer",
            "bank employee",
            "account will be blocked",
            "account blocked",
            "verify my account",
        ]):
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

        if any(word in text for word in [
            "otp",
            "one time password",
            "one-time password",
        ]):
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

        if any(word in text for word in [
            "investment",
            "guaranteed return",
            "double your money",
        ]):
            return IntentResult(
                category=IntentCategory.INVESTMENT_SCAM,
                score=88,
                signals=[
                    "INVESTMENT_PROMISE",
                    "HIGH_RETURN_CLAIM",
                ],
                attributes={
                    "urgency": 0.70,
                    "coercion": 0.50,
                },
                provider="mock",
                model_version="intent-v1",
            )

        if any(word in text for word in [
            "refund",
            "refund fee",
            "refund charge",
        ]):
            return IntentResult(
                category=IntentCategory.REFUND_SCAM,
                score=82,
                signals=[
                    "REFUND_REQUEST",
                    "PAYMENT_DEMAND",
                ],
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
    def __init__(
        self,
        api_key: str | None = None,
        model: str | None = None,
    ):
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        self.model = model or os.getenv(
            "RAKSHA_LLM_MODEL",
            "gpt-5.6-luna",
        )

        self.client = (
            OpenAI(api_key=self.api_key)
            if self.api_key
            else None
        )

        self.fallback = MockIntentProvider()

    def classify(self, reason: str) -> IntentResult:

        # No API key → deterministic fallback
        if not self.client:
            return self.fallback.classify(reason)

        try:
            response = self.client.responses.create(
                model=self.model,
                input=[
                    {
                        "role": "system",
                        "content": """
You are RAKSHA, an intent-classification engine
for a financial safety demonstration.

Analyze the transaction reason and classify the user's
intent.

Allowed categories:

NORMAL
PERSONAL_TRANSFER
PURCHASE
BILL_PAYMENT
BANK_IMPERSONATION
ACCOUNT_SUSPENSION
KYC_SCAM
INVESTMENT_SCAM
REFUND_SCAM
TECH_SUPPORT_SCAM
OTP_SCAM
REMOTE_ACCESS_SCAM
UNKNOWN

Return ONLY valid JSON with this structure:

{
  "category": "ONE_ALLOWED_CATEGORY",
  "score": 0,
  "signals": [],
  "attributes": {
    "urgency": 0.0,
    "authority_impersonation": 0.0,
    "coercion": 0.0
  }
}

Rules:

- score must be between 0 and 100.
- Higher score means stronger evidence of suspicious intent.
- signals must be concise uppercase identifiers.
- attributes must contain values from 0.0 to 1.0.
- Do not invent financial facts.
- Treat threats, urgency, impersonation and pressure
  as important scam indicators.
""",
                    },
                    {
                        "role": "user",
                        "content": reason or "",
                    },
                ],
            )

            raw = response.output_text.strip()

            data = json.loads(raw)

            return IntentResult(
                category=IntentCategory(data["category"]),
                score=max(0, min(100, int(data["score"]))),
                signals=data.get("signals", []),
                attributes=data.get("attributes", {}),
                provider="openai",
                model_version=self.model,
            )

        except Exception:
            # Any API/network/model/JSON failure
            # safely falls back to deterministic behavior.
            return self.fallback.classify(reason)