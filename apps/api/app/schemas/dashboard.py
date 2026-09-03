"""Shared Dashboard Contract."""

from typing import Optional
from pydantic import BaseModel, ConfigDict


class DashboardSummary(BaseModel):
    """Schema for GET /api/v1/dashboard/summary endpoint."""
    
    model_config = ConfigDict(extra="ignore")
    
    total_transactions: int
    flagged_transactions: int
    active_clusters: int


class DashboardTransaction(BaseModel):
    """Schema for GET /api/v1/dashboard/transactions endpoint."""
    
    model_config = ConfigDict(extra="ignore")
    
    transaction_id: int
    status: str
    risk_score: Optional[int] = None


class DashboardCluster(BaseModel):
    """Schema for GET /api/v1/dashboard/clusters endpoint."""
    
    model_config = ConfigDict(extra="ignore")
    
    cluster_id: str
    suspicious_users_count: int
