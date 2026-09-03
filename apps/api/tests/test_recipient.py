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