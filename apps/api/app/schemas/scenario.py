"""Shared Scenario Contract."""

from typing import Any, Dict, Optional
from pydantic import BaseModel, ConfigDict


class ScenarioResponse(BaseModel):
    """Schema for GET /api/v1/scenarios endpoints."""
    
    model_config = ConfigDict(extra="ignore")
    
    id: int
    name: str
    description: Optional[str] = None


class ScenarioRunResponse(BaseModel):
    """Schema for POST /api/v1/scenarios/{scenario_id}/run response."""
    
    model_config = ConfigDict(extra="ignore")
    
    scenario_id: int
    status: str
    result: Optional[Dict[str, Any]] = None
