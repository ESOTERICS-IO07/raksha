"""Behavior Intelligence Engine — Schemas and Enums.

Defines the data contract for the Behavior Engine according to CONTRACTS.md (v1.0.0).
Input: TransactionContext + CustomerBehaviorProfile
Output: BehaviorResult (score: 0-100, signals: list[str], features: dict, model_version: "behavior-v1")
"""

from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Any, Optional, Union
from pydantic import BaseModel, ConfigDict, Field, field_validator


class BehaviorSignal(str, Enum):
    """Machine-readable behavioral anomaly signal enums."""

    AMOUNT_ABOVE_NORMAL = "AMOUNT_ABOVE_NORMAL"
    UNUSUAL_TIME = "UNUSUAL_TIME"
    NEW_BEHAVIOR_PATTERN = "NEW_BEHAVIOR_PATTERN"
    HIGH_TRANSACTION_VELOCITY = "HIGH_TRANSACTION_VELOCITY"
    NEW_DEVICE = "NEW_DEVICE"
    UNUSUAL_LOCATION = "UNUSUAL_LOCATION"
    SPIKE_AMOUNT = "SPIKE_AMOUNT"
    UNFAMILIAR_RECIPIENT_FOR_USER = "UNFAMILIAR_RECIPIENT_FOR_USER"
    OFF_HOURS_TRANSACTION = "OFF_HOURS_TRANSACTION"
    RAPID_SUCCESSION = "RAPID_SUCCESSION"


class LocationContext(BaseModel):
    """Geographic/location context for transaction evaluation."""

    model_config = ConfigDict(extra="ignore")

    country: Optional[str] = "IN"
    region: Optional[str] = None


class TransactionContext(BaseModel):
    """Normalized incoming transaction context sent to intelligence engines."""

    model_config = ConfigDict(extra="ignore")

    transaction_id: Optional[str] = None
    user_id: str
    recipient_id: str
    amount: float
    currency: str = "INR"
    timestamp: Optional[Union[datetime, str]] = None
    device_id: Optional[str] = None
    location: Optional[Union[LocationContext, dict[str, Any], str]] = None
    reason: Optional[str] = None

    @field_validator("amount", mode="before")
    @classmethod
    def validate_amount(cls, v: Any) -> float:
        try:
            val = float(v)
            if val < 0:
                return 0.0
            return val
        except (ValueError, TypeError):
            return 0.0


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
        """Convert features to contract-compliant dictionary with rounded values."""
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
    """Contract-compliant Behavior Engine output schema.

    Must contain score (0-100), signals (list[str]), features (dict), model_version ("behavior-v1").
    Must NEVER contain transaction decisions like ALLOW, VERIFY, STRONG_VERIFY, or HOLD.
    """

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
