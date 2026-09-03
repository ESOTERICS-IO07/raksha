from .config import (
    BEHAVIOR_WEIGHT,
    CRITICAL_HIGH_VALUE,
    HIGH_MAX,
    LOW_MAX,
    MEDIUM_MAX,
    RECIPIENT_WEIGHT,
    INTENT_WEIGHT,
)
from .schemas import RiskAssessment, RiskLevel


class RiskService:

    def calculate(
        self,
        behavior_score: int,
        recipient_score: int,
        intent_score: int,
        intent_category: str | None = None,
        amount: float = 0,
        signals: list[str] | None = None,
    ) -> RiskAssessment:

        behavior_score = max(0, min(100, behavior_score))
        recipient_score = max(0, min(100, recipient_score))
        intent_score = max(0, min(100, intent_score))

        score = round(
            behavior_score * BEHAVIOR_WEIGHT
            + recipient_score * RECIPIENT_WEIGHT
            + intent_score * INTENT_WEIGHT
        )

        combined_signals = list(signals or [])

        # High-confidence safety rule.
        if (
            intent_category == "BANK_IMPERSONATION"
            and amount >= CRITICAL_HIGH_VALUE
            and recipient_score >= 60
        ):
            score = max(score, 81)
            combined_signals.append("HIGH_CONFIDENCE_BANK_IMPERSONATION")

        if score <= LOW_MAX:
            level = RiskLevel.LOW
            action = "ALLOW"
        elif score <= MEDIUM_MAX:
            level = RiskLevel.MEDIUM
            action = "VERIFY"
        elif score <= HIGH_MAX:
            level = RiskLevel.HIGH
            action = "STRONG_VERIFY"
        else:
            level = RiskLevel.CRITICAL
            action = "HOLD"

        return RiskAssessment(
            score=score,
            level=level,
            signals=combined_signals,
            action_recommendation=action,
            engine_version="risk-v1",
        )