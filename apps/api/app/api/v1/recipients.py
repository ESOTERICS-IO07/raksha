"""Recipients API endpoints.

GET /api/v1/recipients/{recipient_id}
GET /api/v1/recipients/{recipient_id}/graph
"""

from __future__ import annotations

import uuid
from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.domain import Recipient
from app.schemas.errors import ErrorDetail, ErrorResponse
from app.services.recipient.adapter import run_recipient_analysis

router = APIRouter(prefix="/recipients", tags=["recipients"])


@router.get("/{recipient_id}")
def get_recipient(recipient_id: int, db: Session = Depends(get_db)) -> dict[str, Any]:
    """Retrieve a recipient by ID."""
    recipient = db.query(Recipient).filter(Recipient.id == recipient_id).first()
    if recipient is None:
        raise HTTPException(
            status_code=404,
            detail=ErrorResponse(
                error=ErrorDetail(
                    code="RECIPIENT_NOT_FOUND",
                    message=f"Recipient '{recipient_id}' does not exist.",
                    request_id=str(uuid.uuid4()),
                )
            ).model_dump(),
        )
    return {"id": recipient.id}


@router.get("/{recipient_id}/graph")
def get_recipient_graph(recipient_id: int, db: Session = Depends(get_db)) -> dict[str, Any]:
    """Return the fraud network graph analysis for a recipient.

    Delegates to Person 3's Recipient Engine via the platform adapter.
    """
    recipient = db.query(Recipient).filter(Recipient.id == recipient_id).first()
    if recipient is None:
        raise HTTPException(
            status_code=404,
            detail=ErrorResponse(
                error=ErrorDetail(
                    code="RECIPIENT_NOT_FOUND",
                    message=f"Recipient '{recipient_id}' does not exist.",
                    request_id=str(uuid.uuid4()),
                )
            ).model_dump(),
        )
    return run_recipient_analysis(str(recipient_id), db)
