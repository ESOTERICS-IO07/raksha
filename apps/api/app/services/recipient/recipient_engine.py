from typing import Any

from app.graph.fraud_graph import build_fraud_graph, analyze_recipient_network


def calculate_recipient_score(
    account_age_days: int,
    sender_count: int,
    previous_flags: int,
    suspicious_transactions: int,
    connected_suspicious_users: int,
) -> tuple[int, list[str]]:
    """
    Calculate recipient risk score from 0 to 100.
    """

    score = 0
    signals = []

    if account_age_days < 30:
        score += 30
        signals.append("NEW_RECIPIENT")

    if sender_count >= 10:
        score += 20
        signals.append("HIGH_SENDER_COUNT")

    if previous_flags > 0:
        score += min(previous_flags * 5, 20)
        signals.append("PREVIOUS_FLAGS")

    if suspicious_transactions >= 2:
        score += 15
        signals.append("SUSPICIOUS_HISTORY")

    if connected_suspicious_users >= 3:
        score += 15
        signals.append("SUSPICIOUS_NETWORK")

    score = min(score, 100)

    return score, signals


def analyze_recipient_from_data(
    recipient_id: str,
    recipient_data: dict[str, Any],
    transactions: list[dict[str, Any]],
) -> dict[str, Any]:
    """
    Perform complete recipient analysis.
    """

    graph = build_fraud_graph(transactions)

    network = analyze_recipient_network(
        graph,
        recipient_id,
    )

    suspicious_transactions = sum(
        1
        for transaction in transactions
        if (
            transaction["recipient"] == recipient_id
            and transaction.get("flagged", False)
        )
    )

    score, signals = calculate_recipient_score(
        account_age_days=recipient_data["account_age_days"],
        sender_count=recipient_data["sender_count"],
        previous_flags=recipient_data["previous_flags"],
        suspicious_transactions=suspicious_transactions,
        connected_suspicious_users=network["connected_suspicious_users"],
    )

    return {
        "score": score,
        "signals": signals,
        "recipient_profile": {
            "account_age_days": recipient_data["account_age_days"],
            "sender_count": recipient_data["sender_count"],
            "previous_flags": recipient_data["previous_flags"],
        },
        "network": network,
        "model_version": "recipient-v1",
    }