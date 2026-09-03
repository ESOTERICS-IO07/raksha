"""Shared Risk Contract."""

from enum import Enum
from typing import List
from pydantic import BaseModel, ConfigDict, Field


class RiskLevel(str, Enum):
    """Categorized risk severity level."""
    
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class ActionRecommendation(str, Enum):
    """Recommended friction action from the Risk Engine."""
    
    ALLOW = "ALLOW"
    VERIFY = "VERIFY"
    STRONG_VERIFY = "STRONG_VERIFY"
    HOLD = "HOLD"


class RiskAssessment(BaseModel):
    """Contract-compliant Risk Engine output schema."""
    
    model_config = ConfigDict(extra="forbid")
    
    score: int = Field(..., ge=0, le=100, description="Final aggregate risk score from 0 to 100")
    level: RiskLevel
    signals: List[str] = Field(..., description="Aggregated risk signals")
    action_recommendation: ActionRecommendation
    engine_version: str = Field(default="risk-v1")
