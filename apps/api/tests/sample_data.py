RECIPIENTS = {
    "R001": {
        "account_age_days": 900,
        "sender_count": 3,
        "previous_flags": 0,
    },
    "R002": {
        "account_age_days": 8,
        "sender_count": 31,
        "previous_flags": 4,
    },
    "R003": {
        "account_age_days": 45,
        "sender_count": 12,
        "previous_flags": 1,
    },
}


TRANSACTIONS = [
    {"sender": "U001", "recipient": "R001", "amount": 850, "flagged": False},
    {"sender": "U002", "recipient": "R001", "amount": 1200, "flagged": False},
    {"sender": "U003", "recipient": "R001", "amount": 900, "flagged": False},

    {"sender": "U010", "recipient": "R002", "amount": 25000, "flagged": True},
    {"sender": "U011", "recipient": "R002", "amount": 18000, "flagged": True},
    {"sender": "U012", "recipient": "R002", "amount": 22000, "flagged": True},
    {"sender": "U013", "recipient": "R002", "amount": 30000, "flagged": True},

    {"sender": "U020", "recipient": "R003", "amount": 5000, "flagged": False},
    {"sender": "U021", "recipient": "R003", "amount": 7000, "flagged": True},
]