from enum import Enum

from pydantic import BaseModel


class FrictionAction(str, Enum):
    ALLOW = "ALLOW"
    VERIFY = "VERIFY"
    STRONG_VERIFY = "STRONG_VERIFY"
    HOLD = "HOLD"


class FrictionDecision(BaseModel):
    action: FrictionAction
    title: str
    message: str