"""Shared Intent Contract."""

from enum import Enum
from typing import Dict, List
from pydantic import BaseModel, ConfigDict, Field


class IntentCategory(str, Enum):
    """Categorized intent of the transaction."""
    
    NORMAL = "NORMAL"
    PERSONAL_TRANSFER = "PERSONAL_TRANSFER"
    PURCHASE = "PURCHASE"
    BILL_PAYMENT = "BILL_PAYMENT"
    BANK_IMPERSONATION = "BANK_IMPERSONATION"
    ACCOUNT_SUSPENSION = "ACCOUNT_SUSPENSION"
    KYC_SCAM = "KYC_SCAM"
    INVESTMENT_SCAM = "INVESTMENT_SCAM"
    REFUND_SCAM = "REFUND_SCAM"
    TECH_SUPPORT_SCAM = "TECH_SUPPORT_SCAM"
    OTP_SCAM = "OTP_SCAM"
    REMOTE_ACCESS_SCAM = "REMOTE_ACCESS_SCAM"
    UNKNOWN = "UNKNOWN"


class IntentResult(BaseModel):
    """Contract-compliant Intent Engine output schema."""
    
    model_config = ConfigDict(extra="forbid")
    
    category: IntentCategory
    score: int = Field(..., ge=0, le=100, description="Intent risk score from 0 to 100")
    signals: List[str] = Field(..., description="Machine-readable signal enums")
    attributes: Dict[str, float] = Field(..., description="Probability attributes (0-1)")
    provider: str = Field(default="mock")
    model_version: str = Field(default="intent-v1")
