"""Transaction API endpoints.

POST /api/v1/transactions/analyze

Integration boundary:
  HTTP request
    → validate via shared TransactionContext schema
    → behavior adapter (P2)
    → recipient adapter (P3)
    → MockIntentProvider (P4 boundary — replace when P4 merges)
    → MockRiskService   (P4 boundary — replace when P4 merges)
    → MockFrictionService (P4 boundary — replace when P4 merges)
    → persist Transaction record to DB
    → return analysis response
"""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.transaction import TransactionContext
from app.schemas.errors import ErrorDetail, ErrorResponse
from app.services.behavior.adapter import run_behavior_analysis
from app.services.recipient.adapter import run_recipient_analysis
from app.services.mocks import MockIntentProvider, MockRiskService, MockFrictionService
from app.models.domain import Transaction, TransactionStatus, User, Recipient

router = APIRouter(prefix="/transactions", tags=["transactions"])


@router.post("/analyze")
def analyze_transaction(
    payload: TransactionContext,
    db: Session = Depends(get_db),
) -> dict[str, Any]:
    """Analyze a transaction through the full RAKSHA intelligence pipeline.

    Validates the transaction context, runs available engines (P2 Behavior,
    P3 Recipient), delegates to P4 mocks for Intent/Risk/Friction, and
    persists the transaction record.
    """
    # Validate that user and recipient exist
    try:
        user_id_int = int(payload.user_id)
        recipient_id_int = int(payload.recipient_id)
    except (ValueError, TypeError):
        raise HTTPException(
            status_code=422,
            detail=ErrorResponse(
                error=ErrorDetail(
                    code="INVALID_ID_FORMAT",
                    message="user_id and recipient_id must be numeric strings.",
                    request_id=str(uuid.uuid4()),
                )
            ).model_dump(),
        )

    user = db.query(User).filter(User.id == user_id_int).first()
    if user is None:
        raise HTTPException(
            status_code=404,
            detail=ErrorResponse(
                error=ErrorDetail(
                    code="USER_NOT_FOUND",
                    message=f"User '{payload.user_id}' does not exist.",
                    request_id=str(uuid.uuid4()),
                )
            ).model_dump(),
        )

    recipient = db.query(Recipient).filter(Recipient.id == recipient_id_int).first()
    if recipient is None:
        raise HTTPException(
            status_code=404,
            detail=ErrorResponse(
                error=ErrorDetail(
                    code="RECIPIENT_NOT_FOUND",
                    message=f"Recipient '{payload.recipient_id}' does not exist.",
                    request_id=str(uuid.uuid4()),
                )
            ).model_dump(),
        )

    # Run intelligence pipeline
    behavior_result = run_behavior_analysis(payload, db)
    recipient_result = run_recipient_analysis(payload.recipient_id, db)
    intent_result = MockIntentProvider(payload)
    risk_result = MockRiskService(behavior_result, recipient_result, intent_result)
    friction_result = MockFrictionService(risk_result)

    # Persist transaction record (PENDING → status from friction action)
    status_map = {
        "ALLOW": TransactionStatus.ALLOWED,
        "VERIFY": TransactionStatus.PENDING,
        "STRONG_VERIFY": TransactionStatus.PENDING,
        "HOLD": TransactionStatus.HELD,
    }
    tx_status = status_map.get(friction_result.get("action", "ALLOW"), TransactionStatus.PENDING)

    db_tx = Transaction(
        user_id=user_id_int,
        recipient_id=recipient_id_int,
        amount=payload.amount,
        currency=payload.currency,
        timestamp=datetime.now(timezone.utc),
        device_id=payload.device_id,
        reason=payload.reason,
        status=tx_status,
    )
    db.add(db_tx)
    db.commit()
    db.refresh(db_tx)

    tx_id = payload.transaction_id or f"TX{db_tx.id}"

    return {
        "transaction_id": tx_id,
        "behavior": behavior_result,
        "recipient": recipient_result,
        "intent": intent_result,
        "risk": risk_result,
        "friction": friction_result,
    }
