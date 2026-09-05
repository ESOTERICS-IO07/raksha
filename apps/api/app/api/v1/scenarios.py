"""Scenarios API endpoints.

GET  /api/v1/scenarios
GET  /api/v1/scenarios/{scenario_id}
POST /api/v1/scenarios/{scenario_id}/run

Scenario execution is designed so that the full intelligence pipeline
(behavior → recipient → intent → risk → friction) can be wired in
once all engines are available. For now, the /run endpoint returns
a structural result showing the analysis boundary.
"""

from __future__ import annotations

import uuid
from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.domain import ScenarioDefinition
from app.schemas.scenario import ScenarioResponse, ScenarioRunResponse
from app.schemas.errors import ErrorDetail, ErrorResponse

router = APIRouter(prefix="/scenarios", tags=["scenarios"])


@router.get("", response_model=list[ScenarioResponse])
def list_scenarios(db: Session = Depends(get_db)) -> list[dict[str, Any]]:
    """List all available scenario definitions."""
    rows = db.query(ScenarioDefinition).all()
    return [{"id": r.id, "name": r.name, "description": r.description} for r in rows]


@router.get("/{scenario_id}", response_model=ScenarioResponse)
def get_scenario(scenario_id: int, db: Session = Depends(get_db)) -> dict[str, Any]:
    """Retrieve a specific scenario definition by ID."""
    row = db.query(ScenarioDefinition).filter(ScenarioDefinition.id == scenario_id).first()
    if row is None:
        raise HTTPException(
            status_code=404,
            detail=ErrorResponse(
                error=ErrorDetail(
                    code="SCENARIO_NOT_FOUND",
                    message=f"Scenario '{scenario_id}' does not exist.",
                    request_id=str(uuid.uuid4()),
                )
            ).model_dump(),
        )
    return {"id": row.id, "name": row.name, "description": row.description}


@router.post("/{scenario_id}/run", response_model=ScenarioRunResponse)
def run_scenario(scenario_id: int, db: Session = Depends(get_db)) -> dict[str, Any]:
    """Execute a scenario through the intelligence pipeline.

    This endpoint represents the integration boundary. When all intelligence
    engines are available the pipeline will be:
      scenario → TransactionContext → behavior → recipient → intent → risk → friction
    """
    row = db.query(ScenarioDefinition).filter(ScenarioDefinition.id == scenario_id).first()
    if row is None:
        raise HTTPException(
            status_code=404,
            detail=ErrorResponse(
                error=ErrorDetail(
                    code="SCENARIO_NOT_FOUND",
                    message=f"Scenario '{scenario_id}' does not exist.",
                    request_id=str(uuid.uuid4()),
                )
            ).model_dump(),
        )

    # Deterministic Demo Scenarios Mapping
    scenarios = {
        1: {"user_id": "1001", "recipient_id": "2001", "amount": 1000, "reason": "Monthly grocery bill"},
        2: {"user_id": "1002", "recipient_id": "2002", "amount": 150000, "reason": "Late night unusual transfer"},
        3: {"user_id": "1003", "recipient_id": "2004", "amount": 5000, "reason": "First payment to this user"},
        4: {"user_id": "1001", "recipient_id": "2020", "amount": 50000, "reason": "Bank officer told me to verify my account"},
        5: {"user_id": "1005", "recipient_id": "2005", "amount": 25000, "reason": "Pay immediately or account suspended"},
        6: {"user_id": "1006", "recipient_id": "2006", "amount": 300000, "reason": "Guaranteed high returns crypto"},
        7: {"user_id": "1007", "recipient_id": "2007", "amount": 40000, "reason": "Refund overpayment send back"},
        8: {"user_id": "1008", "recipient_id": "2020", "amount": 10000, "reason": "Sending money to friend"}
    }

    scenario_data = scenarios.get(scenario_id)
    if not scenario_data:
        from app.models.domain import User, Recipient
        first_u = db.query(User).first()
        first_r = db.query(Recipient).first()
        u_id = str(first_u.id) if first_u else "1001"
        r_id = str(first_r.id) if first_r else "2001"
        scenario_data = {"user_id": u_id, "recipient_id": r_id, "amount": 100, "reason": "Test scenario fallback"}

    from app.schemas.transaction import TransactionContext
    from app.api.v1.transactions import analyze_transaction

    payload = TransactionContext(
        user_id=scenario_data["user_id"],
        recipient_id=scenario_data["recipient_id"],
        amount=scenario_data["amount"],
        reason=scenario_data["reason"]
    )

    result = analyze_transaction(payload, db)

    # Inject frontend display metadata missing from analyze_transaction
    from datetime import datetime, timezone
    result["amount"] = scenario_data["amount"]
    result["reason"] = scenario_data["reason"]
    result["timestamp"] = datetime.now(timezone.utc).isoformat()

    # Map mock names
    recipient_names = {
        "2001": "FreshMart Grocery",
        "2002": "Priya Sharma",
        "2004": "Rahul Electronics",
        "2020": "Unknown Recipient",
    }
    result["recipient_name"] = recipient_names.get(scenario_data["recipient_id"], f"Synthetic Recipient {scenario_data['recipient_id']}")

    return {
        "scenario_id": scenario_id,
        "status": "SUCCESS",
        "result": result,
    }
