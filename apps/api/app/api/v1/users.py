"""Users API endpoints.

GET /api/v1/users/{user_id}
"""

from __future__ import annotations

import uuid
from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.domain import User
from app.schemas.errors import ErrorDetail, ErrorResponse

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/{user_id}")
def get_user(user_id: int, db: Session = Depends(get_db)) -> dict[str, Any]:
    """Retrieve a user by ID."""
    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise HTTPException(
            status_code=404,
            detail=ErrorResponse(
                error=ErrorDetail(
                    code="USER_NOT_FOUND",
                    message=f"User '{user_id}' does not exist.",
                    request_id=str(uuid.uuid4()),
                )
            ).model_dump(),
        )
    return {"id": user.id, "created_at": user.created_at.isoformat()}
