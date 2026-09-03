"""Dashboard API endpoints.

GET /api/v1/dashboard/summary
GET /api/v1/dashboard/transactions
GET /api/v1/dashboard/clusters

Reads from PostgreSQL as the source of truth.
Risk-level fields that depend on Person 4 are clearly marked as pending.
"""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.domain import Transaction, TransactionStatus, FraudCluster

router = APIRouter(prefix="/dashboard", tags=["dashboard"])


@router.get("/summary")
def dashboard_summary(db: Session = Depends(get_db)) -> dict[str, Any]:
    """Return aggregate dashboard statistics from the DB."""
    total = db.query(func.count(Transaction.id)).scalar() or 0
    held = (
        db.query(func.count(Transaction.id))
        .filter(Transaction.status == TransactionStatus.HELD)
        .scalar()
        or 0
    )
    clusters = db.query(func.count(FraudCluster.id)).scalar() or 0

    return {
        "total_transactions": total,
        "flagged_transactions": held,
        "active_clusters": clusters,
    }


@router.get("/transactions")
def dashboard_transactions(
    limit: int = 50,
    db: Session = Depends(get_db),
) -> list[dict[str, Any]]:
    """Return recent transactions for the dashboard."""
    rows = (
        db.query(Transaction)
        .order_by(Transaction.created_at.desc())
        .limit(limit)
        .all()
    )
    return [
        {
            "transaction_id": r.id,
            "status": r.status.value,
            "amount": float(r.amount),
            "currency": r.currency,
            "risk_score": None,  # Populated after P4 Risk Engine is integrated
        }
        for r in rows
    ]


@router.get("/clusters")
def dashboard_clusters(db: Session = Depends(get_db)) -> list[dict[str, Any]]:
    """Return known fraud clusters from the DB."""
    rows = db.query(FraudCluster).all()
    return [
        {
            "cluster_id": f"CLUSTER-{r.recipient_id}",
            "suspicious_users_count": 0,  # Populated after P3 graph data is persisted
        }
        for r in rows
    ]
