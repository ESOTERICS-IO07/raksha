"""Platform adapter for Person 2's Behavior Engine.

Isolates database/API concerns from the Behavior Engine implementation.
Person 2's engine lives in app.services.behavior.engine and must not be modified.

Translation responsibilities:
- Build CustomerBehaviorProfile from DB BehaviorProfile row
- Pass TransactionContext to the engine
- Return BehaviorResult (or a compatible dict)
"""

from __future__ import annotations

from typing import Any, Optional, TYPE_CHECKING

from app.schemas.behavior import CustomerBehaviorProfile, BehaviorResult

if TYPE_CHECKING:
    from sqlalchemy.orm import Session


def _build_profile_from_db(db_profile: Any, user_id: str) -> CustomerBehaviorProfile:
    """Convert a SQLAlchemy BehaviorProfile row into a CustomerBehaviorProfile.

    When the Behavior Engine branch is merged, this will map persisted profile
    fields onto the model. For now, returns a cold-start default.
    """
    return CustomerBehaviorProfile(user_id=user_id)


def run_behavior_analysis(
    tx_context: Any,
    db: "Session",
) -> dict[str, Any]:
    """Run the Behavior Engine for a given TransactionContext.

    Fetches the user's persisted BehaviorProfile from the DB (if present),
    builds the CustomerBehaviorProfile, then delegates to Person 2's engine.

    Returns a contract-compliant BehaviorResult dict.
    """
    try:
        # Lazy import so the adapter doesn't hard-fail if P2 is not yet merged
        from app.services.behavior.engine import analyze_behavior  # type: ignore

        from app.models.domain import BehaviorProfile as DBBehaviorProfile

        db_profile = (
            db.query(DBBehaviorProfile)
            .filter(DBBehaviorProfile.user_id == int(tx_context.user_id))
            .first()
        )
        profile = _build_profile_from_db(db_profile, str(tx_context.user_id))
        return analyze_behavior(tx_context, profile)

    except ImportError:
        # P2 not merged yet — return a clearly-labelled stub result
        return BehaviorResult(
            score=0,
            signals=[],
            features={"stub": True},
            model_version="behavior-v1",
        ).model_dump()
