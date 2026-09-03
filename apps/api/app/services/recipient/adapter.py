"""Platform adapter for Person 3's Recipient Engine.

Isolates database/API concerns from the Recipient Engine.
Person 3's engine lives in app.services.recipient.recipient_engine and must not be modified.

Key translation responsibilities:
- DB fields (user_id, recipient_id) → P3 graph format (sender, recipient)
- Fraud flag state from fraud_flags table → boolean "flagged" on each tx dict
- Recipient profile fields from DB Recipient row → recipient_data dict
"""

from __future__ import annotations

from typing import Any, Optional, TYPE_CHECKING

from app.schemas.recipient import RecipientResult

if TYPE_CHECKING:
    from sqlalchemy.orm import Session


def _build_transaction_dicts(
    transactions: list[Any],
    flagged_tx_ids: set[int],
) -> list[dict[str, Any]]:
    """Convert SQLAlchemy Transaction rows to the format P3's engine expects.

    DB columns:           → P3 graph format:
      user_id (int)       →   sender (str)
      recipient_id (int)  →   recipient (str)
      amount              →   amount
      id (int)            →   flagged (bool, aggregated from fraud_flags)
    """
    result = []
    for tx in transactions:
        result.append(
            {
                "sender": str(tx.user_id),
                "recipient": str(tx.recipient_id),
                "amount": float(tx.amount),
                "flagged": tx.id in flagged_tx_ids,
            }
        )
    return result


def _build_recipient_data(db_recipient: Any) -> dict[str, Any]:
    """Build the recipient_data dict P3's engine expects from a DB Recipient row.

    The DB Recipient model is currently minimal (id only). This will be extended
    when recipient profile fields are persisted. For now returns safe defaults
    that the engine can work with.
    """
    # Count fraud flags relationally
    previous_flags = len(db_recipient.fraud_flags) if db_recipient.fraud_flags else 0

    # Count unique senders from transactions
    sender_ids = {tx.user_id for tx in db_recipient.transactions} if db_recipient.transactions else set()

    return {
        "account_age_days": 0,  # Will be populated from extended Recipient model
        "sender_count": len(sender_ids),
        "previous_flags": previous_flags,
    }


def run_recipient_analysis(
    recipient_id: str,
    db: "Session",
) -> dict[str, Any]:
    """Run the Recipient Engine for a given recipient_id.

    1. Loads the Recipient and related transactions from DB
    2. Loads fraud_flags to determine which transactions are flagged
    3. Translates DB field names → P3 engine format
    4. Delegates to Person 3's engine
    5. Returns a RecipientResult-compatible dict
    """
    from app.models.domain import Recipient, Transaction, FraudFlag

    try:
        r_id_int = int(recipient_id)
    except (ValueError, TypeError):
        return RecipientResult(
            score=0,
            signals=["INVALID_RECIPIENT_ID"],
            recipient_profile={"account_age_days": 0, "sender_count": 0, "previous_flags": 0},
            network={"cluster_id": None, "connected_suspicious_users": 0},
            model_version="recipient-v1",
        ).model_dump()

    db_recipient = db.query(Recipient).filter(Recipient.id == r_id_int).first()
    if db_recipient is None:
        return RecipientResult(
            score=0,
            signals=[],
            recipient_profile={"account_age_days": 0, "sender_count": 0, "previous_flags": 0},
            network={"cluster_id": None, "connected_suspicious_users": 0},
            model_version="recipient-v1",
        ).model_dump()

    # Build flagged tx set from fraud_flags table (relational, not a column)
    all_tx_ids = [tx.id for tx in db_recipient.transactions] if db_recipient.transactions else []
    flagged_tx_ids: set[int] = set()
    if all_tx_ids:
        flags = db.query(FraudFlag).filter(FraudFlag.recipient_id == r_id_int).all()
        # For now, flag all transactions of a flagged recipient
        if flags:
            flagged_tx_ids = set(all_tx_ids)

    tx_dicts = _build_transaction_dicts(
        db_recipient.transactions or [], flagged_tx_ids
    )
    recipient_data = _build_recipient_data(db_recipient)

    try:
        from app.services.recipient.recipient_engine import analyze_recipient_from_data  # type: ignore

        return analyze_recipient_from_data(
            recipient_id=str(r_id_int),
            recipient_data=recipient_data,
            transactions=tx_dicts,
        )
    except ImportError:
        # P3 not merged yet — return stub
        return RecipientResult(
            score=0,
            signals=[],
            recipient_profile=recipient_data,
            network={"cluster_id": f"CLUSTER-{r_id_int}", "connected_suspicious_users": 0},
            model_version="recipient-v1",
        ).model_dump()
