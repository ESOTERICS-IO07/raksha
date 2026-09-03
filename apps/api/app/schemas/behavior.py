"""Shared Behavior Contract.

Provides the canonical Behavior models for the platform boundary.
Uses a compatibility re-export strategy to yield to the Behavior Engine's
implementation once it is merged, avoiding divergent models.
"""

from typing import Any, Optional
from pydantic import BaseModel, ConfigDict, Field, field_validator

try:
    from app.services.behavior.schemas import ( # type: ignore
        BehaviorFeatures,
        BehaviorResult,
        CustomerBehaviorProfile,
    )
except ImportError:
    # Fallback strict definitions until feature/behavior-engine is merged
    class CustomerBehaviorProfile(BaseModel):
        """Customer historical behavioral baseline profile."""

        model_config = ConfigDict(extra="ignore")

        user_id: str = ""
        avg_amount: float = 0.0
        std_amount: float = 0.0
        min_amount: float = 0.0
        max_amount: float = 0.0
        usual_hours: list[int] = Field(default_factory=list)
        frequent_recipients: list[str] = Field(default_factory=list)
        known_devices: list[str] = Field(default_factory=list)
        known_locations: list[str] = Field(default_factory=list)
        avg_daily_transactions: float = 1.0
        recent_transaction_count_1h: int = 0
        recent_transaction_count_24h: int = 0
        historical_transactions: Optional[list[dict[str, Any]]] = None

    class BehaviorFeatures(BaseModel):
        """Extracted numeric & contextual features used for ML inference and rule scoring."""

        model_config = ConfigDict(extra="allow")

        amount_deviation: float = 0.0
        amount_to_avg_ratio: float = 1.0
        hour_deviation: float = 0.0
        recipient_frequency: int = 0
        is_new_recipient: bool = False
        is_new_device: bool = False
        is_new_location: bool = False
        velocity_1h: int = 0
        velocity_24h: int = 0
        isolation_forest_anomaly_score: float = 0.0

        def to_contract_dict(self) -> dict[str, Any]:
            return {
                "amount_deviation": round(float(self.amount_deviation), 2),
                "hour_deviation": round(float(self.hour_deviation), 2),
                "recipient_frequency": int(self.recipient_frequency),
                "amount_to_avg_ratio": round(float(self.amount_to_avg_ratio), 2),
                "is_new_recipient": bool(self.is_new_recipient),
                "is_new_device": bool(self.is_new_device),
                "is_new_location": bool(self.is_new_location),
                "velocity_1h": int(self.velocity_1h),
                "velocity_24h": int(self.velocity_24h),
                "isolation_forest_anomaly_score": round(float(self.isolation_forest_anomaly_score), 4),
            }

    class BehaviorResult(BaseModel):
        """Contract-compliant Behavior Engine output schema."""

        model_config = ConfigDict(extra="forbid")

        score: int = Field(..., ge=0, le=100, description="Anomaly score from 0 to 100")
        signals: list[str] = Field(default_factory=list, description="Machine-readable signal enums")
        features: dict[str, Any] = Field(default_factory=dict, description="Extracted feature details")
        model_version: str = Field(default="behavior-v1", description="Fixed model version identifier")

        @field_validator("score", mode="before")
        @classmethod
        def clamp_and_round_score(cls, v: Any) -> int:
            try:
                val = round(float(v))
                return max(0, min(100, int(val)))
            except (ValueError, TypeError):
                return 0

__all__ = ["BehaviorFeatures", "BehaviorResult", "CustomerBehaviorProfile"]
