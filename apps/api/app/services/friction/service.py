from .schemas import FrictionAction, FrictionDecision


class FrictionService:

    def decide(self, risk_level: str) -> FrictionDecision:

        mapping = {
            "LOW": FrictionDecision(
                action=FrictionAction.ALLOW,
                title="Payment Approved",
                message="This payment appears consistent with normal activity.",
            ),
            "MEDIUM": FrictionDecision(
                action=FrictionAction.VERIFY,
                title="Please Verify",
                message="Please verify this payment before continuing.",
            ),
            "HIGH": FrictionDecision(
                action=FrictionAction.STRONG_VERIFY,
                title="Additional Verification Required",
                message="This payment is unusual and requires additional verification.",
            ),
            "CRITICAL": FrictionDecision(
                action=FrictionAction.HOLD,
                title="Payment Paused",
                message="This payment may involve a scam or manipulation attempt.",
            ),
        }

        return mapping.get(
            risk_level,
            mapping["CRITICAL"],
        )