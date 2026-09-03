"""Schema tests for shared Platform layer."""

import pytest
from pydantic import ValidationError
from datetime import datetime

from app.schemas.transaction import TransactionContext, LocationContext
from app.schemas.behavior import BehaviorResult, CustomerBehaviorProfile, BehaviorFeatures
from app.schemas.recipient import RecipientResult, RecipientProfile, RecipientNetwork
from app.schemas.intent import IntentResult, IntentCategory
from app.schemas.risk import RiskAssessment, RiskLevel, ActionRecommendation
from app.schemas.friction import FrictionDecision, FrictionAction
from app.schemas.errors import ErrorResponse, ErrorDetail


# --- TransactionContext ---

def test_valid_transaction_context():
    data = {
        "transaction_id": "TX1001",
        "user_id": "U001",
        "recipient_id": "R014",
        "amount": 50000,
        "currency": "INR",
        "timestamp": "2026-09-03T23:43:00+05:30",
        "device_id": "D001",
        "location": {"country": "IN", "region": "TN"},
        "reason": "Bank officer told me to verify my account",
    }
    tx = TransactionContext(**data)
    assert tx.user_id == "U001"
    assert tx.amount == 50000.0
    assert tx.currency == "INR"

def test_invalid_transaction_context_amount():
    data = {"user_id": "U001", "recipient_id": "R014", "amount": "not-a-number"}
    tx = TransactionContext(**data)
    # field_validator coerces to 0.0 on failure
    assert tx.amount == 0.0

def test_transaction_context_negative_amount_clipped():
    data = {"user_id": "U001", "recipient_id": "R014", "amount": -500}
    tx = TransactionContext(**data)
    assert tx.amount == 0.0


# --- BehaviorResult ---

def test_valid_behavior_result():
    data = {
        "score": 87,
        "signals": ["AMOUNT_ABOVE_NORMAL", "UNUSUAL_TIME", "NEW_BEHAVIOR_PATTERN"],
        "features": {"amount_deviation": 4.8},
        "model_version": "behavior-v1",
    }
    result = BehaviorResult(**data)
    assert result.score == 87
    assert result.model_version == "behavior-v1"

def test_invalid_behavior_result_score():
    data = {"score": 200, "signals": [], "features": {}, "model_version": "behavior-v1"}
    result = BehaviorResult(**data)
    # Validator clamps to 100
    assert result.score == 100


def test_valid_recipient_result():
    data = {
        "score": 76,
        "signals": ["NEW_RECIPIENT", "HIGH_SENDER_COUNT", "SUSPICIOUS_NETWORK"],
        "recipient_profile": {
            "account_age_days": 8,
            "sender_count": 31,
            "previous_flags": 4
        },
        "network": {
            "cluster_id": "CLUSTER-17",
            "connected_suspicious_users": 4
        },
        "model_version": "recipient-v1"
    }
    result = RecipientResult(**data)
    assert result.score == 76
    assert result.network.cluster_id == "CLUSTER-17"

def test_invalid_recipient_result_score():
    data = {
        "score": 150, # invalid
        "signals": [],
        "recipient_profile": {"account_age_days": 1, "sender_count": 1, "previous_flags": 0},
        "network": {"cluster_id": "C", "connected_suspicious_users": 1},
        "model_version": "recipient-v1"
    }
    with pytest.raises(ValidationError):
        RecipientResult(**data)

def test_valid_recipient_network_with_extra():
    # P3 engine sends network_size
    net = RecipientNetwork(cluster_id="C", connected_suspicious_users=2, network_size=10)
    assert net.network_size == 10

def test_valid_intent_categories():
    data = {
        "category": "BANK_IMPERSONATION",
        "score": 94,
        "signals": ["AUTHORITY_IMPERSONATION"],
        "attributes": {"urgency": 0.94},
        "provider": "mock",
        "model_version": "intent-v1"
    }
    result = IntentResult(**data)
    assert result.category == IntentCategory.BANK_IMPERSONATION

def test_invalid_intent_category():
    data = {
        "category": "FAKE_SCAM", # Invalid
        "score": 50,
        "signals": [],
        "attributes": {},
        "provider": "mock",
        "model_version": "intent-v1"
    }
    with pytest.raises(ValidationError):
        IntentResult(**data)

def test_valid_risk_assessment():
    data = {
        "score": 91,
        "level": "CRITICAL",
        "signals": ["AMOUNT_ABOVE_NORMAL"],
        "action_recommendation": "HOLD",
        "engine_version": "risk-v1"
    }
    result = RiskAssessment(**data)
    assert result.level == RiskLevel.CRITICAL
    assert result.action_recommendation == ActionRecommendation.HOLD

def test_invalid_risk_level():
    data = {
        "score": 91,
        "level": "SUPER_HIGH", # Invalid
        "signals": [],
        "action_recommendation": "HOLD",
        "engine_version": "risk-v1"
    }
    with pytest.raises(ValidationError):
        RiskAssessment(**data)

def test_valid_friction_decision():
    data = {
        "action": "HOLD",
        "title": "Payment Paused",
        "message": "This payment resembles an account-verification scam."
    }
    result = FrictionDecision(**data)
    assert result.action == FrictionAction.HOLD

def test_invalid_friction_action():
    data = {
        "action": "BLOCK", # Invalid
        "title": "Payment Paused",
        "message": "Blocked"
    }
    with pytest.raises(ValidationError):
        FrictionDecision(**data)

def test_valid_error_response():
    data = {
        "error": {
            "code": "RECIPIENT_NOT_FOUND",
            "message": "Recipient does not exist.",
            "request_id": "REQ123"
        }
    }
    result = ErrorResponse(**data)
    assert result.error.code == "RECIPIENT_NOT_FOUND"

