"""Shared Recipient Contract.

Formalizes the Recipient Engine output for platform boundaries.
"""

from typing import List, Optional
from pydantic import BaseModel, ConfigDict, Field


class RecipientProfile(BaseModel):
    """Recipient historical risk profile."""
    
    model_config = ConfigDict(extra="ignore")
    
    account_age_days: int
    sender_count: int
    previous_flags: int


class RecipientNetwork(BaseModel):
    """Fraud graph network topology features."""
    
    model_config = ConfigDict(extra="allow")  # Allows network_size from P3
    
    cluster_id: Optional[str] = None
    connected_suspicious_users: int
    network_size: Optional[int] = None  # Compatible with P3 graph output


class RecipientResult(BaseModel):
    """Contract-compliant Recipient Engine output schema."""
    
    model_config = ConfigDict(extra="forbid")
    
    score: int = Field(..., ge=0, le=100, description="Recipient risk score from 0 to 100")
    signals: List[str] = Field(..., description="Machine-readable signal enums")
    recipient_profile: RecipientProfile
    network: RecipientNetwork
    model_version: str = Field(default="recipient-v1")
