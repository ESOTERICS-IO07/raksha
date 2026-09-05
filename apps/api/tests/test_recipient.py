from app.services.recipient.recipient_engine import (
    calculate_recipient_score,
    analyze_recipient_from_data,
)

from tests.sample_data import RECIPIENTS, TRANSACTIONS


def test_score_range():
    score, _ = calculate_recipient_score(
        account_age_days=900,
        sender_count=3,
        previous_flags=0,
        suspicious_transactions=0,
        connected_suspicious_users=0,
    )

    assert 0 <= score <= 100


def test_new_recipient():
    _, signals = calculate_recipient_score(
        account_age_days=8,
        sender_count=3,
        previous_flags=0,
        suspicious_transactions=0,
        connected_suspicious_users=0,
    )

    assert "NEW_RECIPIENT" in signals


def test_high_sender_count():
    _, signals = calculate_recipient_score(
        account_age_days=900,
        sender_count=31,
        previous_flags=0,
        suspicious_transactions=0,
        connected_suspicious_users=0,
    )

    assert "HIGH_SENDER_COUNT" in signals


def test_suspicious_network():
    _, signals = calculate_recipient_score(
        account_age_days=900,
        sender_count=3,
        previous_flags=0,
        suspicious_transactions=0,
        connected_suspicious_users=4,
    )

    assert "SUSPICIOUS_NETWORK" in signals


def test_full_recipient_analysis():
    result = analyze_recipient_from_data(
        recipient_id="R002",
        recipient_data=RECIPIENTS["R002"],
        transactions=TRANSACTIONS,
    )

    assert 0 <= result["score"] <= 100
    assert "signals" in result
    assert "recipient_profile" in result
    assert "network" in result
    assert result["model_version"] == "recipient-v1"


def test_adapter_r020_connected_network():
    from unittest.mock import MagicMock
    from app.services.recipient.adapter import run_recipient_analysis
    from datetime import datetime, timezone, timedelta

    db_mock = MagicMock()

    mock_recipient = MagicMock()
    mock_recipient.id = 2020

    mock_flag = MagicMock()
    mock_recipient.fraud_flags = [mock_flag, mock_flag, mock_flag]

    now = datetime.now(timezone.utc)
    txs = []
    for i, user_id in enumerate([11, 12, 13, 14]):
        tx = MagicMock()
        tx.id = 100 + i
        tx.user_id = user_id
        tx.recipient_id = 2020
        tx.amount = 50000
        tx.timestamp = now - timedelta(days=50 - i) # 50, 49, 48, 47 days ago
        txs.append(tx)

    mock_recipient.transactions = txs

    db_mock.query().filter().first.return_value = mock_recipient
    db_mock.query().filter().all.return_value = [mock_flag]

    result = run_recipient_analysis("2020", db_mock)

    # 1. Output remains contract-compatible
    assert "score" in result
    assert "signals" in result
    assert "recipient_profile" in result
    assert "network" in result

    # 2. Account age is calculated correctly (oldest is 50 days ago)
    assert result["recipient_profile"]["account_age_days"] == 50

    # 3. R020's connected-user network is represented correctly
    # 4 users, all flagged because of recipient-level fallback
    assert result["network"]["connected_suspicious_users"] == 4
    assert result["network"]["cluster_id"] == "CLUSTER-2020"
