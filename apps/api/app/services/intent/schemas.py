from enum import Enum
from typing import Dict, List

from pydantic import BaseModel, Field


class IntentCategory(str, Enum):
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
    category: IntentCategory
    score: int = Field(ge=0, le=100)
    signals: List[str] = Field(default_factory=list)
    attributes: Dict[str, float] = Field(default_factory=dict)
    provider: str
    model_version: str