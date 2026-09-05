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

# Import actual P4 services
from app.services.intent.providers import LLMProvider
from app.services.intent.service import IntentService
from app.services.risk.service import RiskService
from app.services.friction.service import FrictionService

# Import canonical schemas for validation
from app.schemas.intent import IntentResult as CanonicalIntentResult
from app.schemas.risk import RiskAssessment as CanonicalRiskAssessment
from app.schemas.friction import FrictionDecision as CanonicalFrictionDecision

# Import domain models for DB persistence
from app.models.domain import (
    Transaction,
    TransactionStatus,
    User,
    Recipient,
    IntentResult as DBIntentResult,
    RiskAssessment as DBRiskAssessment,
    FrictionDecision as DBFrictionDecision,
)

router = APIRouter(prefix="/transactions", tags=["transactions"])


@router.post("/analyze")
def analyze_transaction(
    payload: TransactionContext,
    db: Session = Depends(get_db),
) -> dict[str, Any]:
    """Analyze a transaction through the full RAKSHA intelligence pipeline.

    Validates the transaction context, runs available engines (P2 Behavior,
    P3 Recipient, P4 Intent, P4 Risk, P4 Friction), validates against 
    canonical schemas, and persists the transaction record and outputs.
    """
    # Validate that user and recipient exist
    def parse_id(raw_id: str, prefix: str, offset: int) -> int:
        try:
            return int(raw_id)
        except ValueError:
            if isinstance(raw_id, str) and raw_id.upper().startswith(prefix.upper()):
                try:
                    return int(raw_id[1:]) + offset
                except ValueError:
                    pass
            raise ValueError(f"Invalid ID format for {prefix}")

    try:
        user_id_int = parse_id(payload.user_id, "U", 1000)
        recipient_id_int = parse_id(payload.recipient_id, "R", 2000)
    except (ValueError, TypeError):
        raise HTTPException(
            status_code=422,
            detail=ErrorResponse(
                error=ErrorDetail(
                    code="INVALID_ID_FORMAT",
                    message="user_id and recipient_id must be numeric strings or start with U/R.",
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

    # 1. Run P2 Behavior and P3 Recipient (Existing)
    # Convert IDs to internal numeric strings so P2/P3 adapters don't fail
    payload.user_id = str(user_id_int)
    payload.recipient_id = str(recipient_id_int)

    behavior_result = run_behavior_analysis(payload, db)
    recipient_result = run_recipient_analysis(payload.recipient_id, db, current_user_id=payload.user_id)

    # 2. Run P4 Intent
    intent_svc = IntentService(provider=LLMProvider())
    p4_intent = intent_svc.analyze(payload.reason)
    canonical_intent = CanonicalIntentResult(**p4_intent.model_dump())

    # 3. Run P4 Risk
    behavior_score = behavior_result.get("score", 0)
    recipient_score = recipient_result.get("score", 0)
    intent_score = canonical_intent.score
    intent_category = canonical_intent.category.value
    amount = float(payload.amount)
    
    combined_signals = (
        behavior_result.get("signals", [])
        + recipient_result.get("signals", [])
        + canonical_intent.signals
    )

    risk_svc = RiskService()
    p4_risk = risk_svc.calculate(
        behavior_score=behavior_score,
        recipient_score=recipient_score,
        intent_score=intent_score,
        intent_category=intent_category,
        amount=amount,
        signals=combined_signals,
    )
    canonical_risk = CanonicalRiskAssessment(**p4_risk.model_dump())

    # 4. Run P4 Friction
    friction_svc = FrictionService()
    p4_friction = friction_svc.decide(canonical_risk.level.value)
    canonical_friction = CanonicalFrictionDecision(**p4_friction.model_dump())

    # 5. Map status
    status_map = {
        "ALLOW": TransactionStatus.ALLOWED,
        "VERIFY": TransactionStatus.PENDING,
        "STRONG_VERIFY": TransactionStatus.PENDING,
        "HOLD": TransactionStatus.HELD,
    }
    tx_status = status_map.get(canonical_friction.action.value, TransactionStatus.PENDING)

    # 6. Persist transaction and outputs
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
    
    # Attach result models
    db_tx.intent_result = DBIntentResult(
        category=canonical_intent.category.value,
        score=canonical_intent.score,
        signals=canonical_intent.signals,
        attributes=canonical_intent.attributes,
        provider=canonical_intent.provider,
        model_version=canonical_intent.model_version,
    )
    db_tx.risk_assessment = DBRiskAssessment(
        score=canonical_risk.score,
        level=canonical_risk.level.value,
        signals=canonical_risk.signals,
        action_recommendation=canonical_risk.action_recommendation.value,
        engine_version=canonical_risk.engine_version,
    )
    db_tx.friction_decision = DBFrictionDecision(
        action=canonical_friction.action.value,
        title=canonical_friction.title,
        message=canonical_friction.message,
    )

    db.add(db_tx)
    db.commit()
    db.refresh(db_tx)

    tx_id = payload.transaction_id or f"TX{db_tx.id}"

    return {
        "transaction_id": tx_id,
        "behavior": behavior_result,
        "recipient": recipient_result,
        "intent": canonical_intent.model_dump(),
        "risk": canonical_risk.model_dump(),
        "friction": canonical_friction.model_dump(),
    }
