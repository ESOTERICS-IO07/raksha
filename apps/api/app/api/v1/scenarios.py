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

    # TODO: Wire full pipeline when P4 is merged
    return {
        "scenario_id": scenario_id,
        "status": "PENDING_FULL_PIPELINE",
        "result": {
            "scenario_name": row.name,
            "note": "Full intelligence pipeline will be wired after Person 4 integration.",
        },
    }
