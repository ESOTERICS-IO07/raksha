"""Shared Transaction Contract.

Provides the canonical TransactionContext for the platform boundary.
Uses a compatibility re-export strategy to yield to the Behavior Engine's
implementation once it is merged, avoiding divergent models.
"""

from datetime import datetime
from typing import Any, Optional, Union
from pydantic import BaseModel, ConfigDict, field_validator

try:
    from app.services.behavior.schemas import LocationContext, TransactionContext # type: ignore
except ImportError:
    # Fallback strict definitions until feature/behavior-engine is merged
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

__all__ = ["LocationContext", "TransactionContext"]
