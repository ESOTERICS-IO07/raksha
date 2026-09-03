import json
import random
from datetime import datetime, timedelta, timezone

def generate_graph():
    # We use fixed random seed for reproducibility
    random.seed(42)

    users = []
    recipients = []
    transactions = []
    fraud_flags = []
    scenarios = []

    # Semantic to Integer ID mappings (safe high range to avoid conflicts)
    user_ids = {f"SYNTHETIC_USER_{i:03d}": 1000 + i for i in range(1, 15)}
    recipient_ids = {f"SYNTHETIC_RECIPIENT_{i:03d}": 2000 + i for i in range(1, 25)}

    for u_name, u_id in user_ids.items():
        users.append({"id": u_id, "semantic_name": u_name})
    
    for r_name, r_id in recipient_ids.items():
        recipients.append({"id": r_id, "semantic_name": r_name})

    now = datetime.now(timezone.utc)

    tx_id_counter = 50000

    # 1. Normal historical behavior for users 1-8
    # Generating ~200 transactions
    for i in range(1, 9):
        u_id = user_ids[f"SYNTHETIC_USER_{i:03d}"]
        # Each user has a favorite recipient
        fav_r_id = recipient_ids[f"SYNTHETIC_RECIPIENT_{i:03d}"]
        
        for _ in range(25):
            days_ago = random.randint(1, 180)
            tx_time = now - timedelta(days=days_ago)
            amount = round(random.uniform(100.0, 500.0), 2)
            transactions.append({
                "id": tx_id_counter,
                "user_id": u_id,
                "recipient_id": fav_r_id,
                "amount": amount,
                "currency": "INR",
                "timestamp": tx_time.isoformat(),
                "device_id": f"DEV_{u_id}",
                "reason": "grocery",
                "status": "ALLOWED"
            })
            tx_id_counter += 1

    # 2. Required Fraud Network
    # A->X 50k, B->X 30k, C->X 70k, D->X 15k
    fraud_recipient_name = "SYNTHETIC_RECIPIENT_020"
    fraud_recipient_id = recipient_ids[fraud_recipient_name]
    
    # Give recipient suspicious evidence (fraud flags)
    for i in range(3):
        fraud_flags.append({
            "id": 8000 + i,
            "recipient_id": fraud_recipient_id
        })

    network_amounts = [
        ("SYNTHETIC_USER_011", 50000),
        ("SYNTHETIC_USER_012", 30000),
        ("SYNTHETIC_USER_013", 70000),
        ("SYNTHETIC_USER_014", 15000)
    ]

    for u_name, amount in network_amounts:
        u_id = user_ids[u_name]
        transactions.append({
            "id": tx_id_counter,
            "user_id": u_id,
            "recipient_id": fraud_recipient_id,
            "amount": amount,
            "currency": "INR",
            "timestamp": (now - timedelta(hours=1)).isoformat(),
            "device_id": f"DEV_{u_id}",
            "reason": "urgent transfer",
            "status": "ALLOWED"
        })
        tx_id_counter += 1

    # Add Scenarios definitions for Scenario runner (mapping payload for scenario execution)
    scenarios.append({
        "id": 9001,
        "name": "BANK_IMPERSONATION",
        "description": "Simulates a bank impersonation call with high urgency.",
        "payload": {
            "user_id": user_ids["SYNTHETIC_USER_001"],  # normal user baseline
            "recipient_id": fraud_recipient_id,         # highly suspicious recipient
            "amount": 45000,                            # large unusual amount for this user
            "currency": "INR",
            "reason": "A bank officer told me to transfer this immediately or my account will be blocked.",
            "device_id": f"DEV_{user_ids['SYNTHETIC_USER_001']}"
        }
    })

    scenarios.append({
        "id": 9002,
        "name": "NORMAL_PAYMENT",
        "description": "Routine payment to an existing trusted recipient.",
        "payload": {
            "user_id": user_ids["SYNTHETIC_USER_002"],
            "recipient_id": recipient_ids["SYNTHETIC_RECIPIENT_002"],
            "amount": 250,
            "currency": "INR",
            "reason": "lunch",
            "device_id": f"DEV_{user_ids['SYNTHETIC_USER_002']}"
        }
    })

    graph = {
        "users": users,
        "recipients": recipients,
        "transactions": transactions,
        "fraud_flags": fraud_flags,
        "scenarios": scenarios
    }

    import os
    os.makedirs("data/seed", exist_ok=True)
    os.makedirs("data/scenarios", exist_ok=True)

    with open("data/seed/demo_graph.json", "w") as f:
        json.dump(graph, f, indent=2)

if __name__ == "__main__":
    generate_graph()
