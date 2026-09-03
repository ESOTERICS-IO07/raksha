"""Shared Friction Contract."""

from enum import Enum
from pydantic import BaseModel, ConfigDict


class FrictionAction(str, Enum):
    """Final friction action decided by the Adaptive Friction Engine."""
    
    ALLOW = "ALLOW"
    VERIFY = "VERIFY"
    STRONG_VERIFY = "STRONG_VERIFY"
    HOLD = "HOLD"


class FrictionDecision(BaseModel):
    """Contract-compliant Adaptive Friction output schema."""
    
    model_config = ConfigDict(extra="forbid")
    
    action: FrictionAction
    title: str
    message: str
