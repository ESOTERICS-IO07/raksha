"""Shared Errors Contract."""

from typing import Optional
from pydantic import BaseModel, ConfigDict


class ErrorDetail(BaseModel):
    """Detailed error representation."""
    
    model_config = ConfigDict(extra="ignore")
    
    code: str
    message: str
    request_id: Optional[str] = None


class ErrorResponse(BaseModel):
    """Standardized API error response wrapper."""
    
    model_config = ConfigDict(extra="ignore")
    
    error: ErrorDetail
