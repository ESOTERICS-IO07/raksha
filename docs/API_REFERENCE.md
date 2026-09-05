# RAKSHA API Reference

Base URL in local development:

``` text
http://127.0.0.1:8000
```

Base API path:

``` text
/api/v1
```

Swagger:

``` text
/docs
```

## Analyze transaction

``` http
POST /api/v1/transactions/analyze
Content-Type: application/json
```

Example:

``` json
{
  "user_id": "U001",
  "recipient_id": "R020",
  "amount": 50000,
  "currency": "INR",
  "reason": "Bank officer told me to verify my account"
}
```

The response contains:

``` text
transaction_id
behavior
recipient
intent
risk
friction
```

## Scenarios

``` http
GET /api/v1/scenarios
GET /api/v1/scenarios/{scenario_id}
POST /api/v1/scenarios/{scenario_id}/run
```

The seeded scenario names are:

``` text
NORMAL_PAYMENT
UNUSUAL_PAYMENT
NEW_RECIPIENT
BANK_IMPERSONATION
ACCOUNT_SUSPENSION
INVESTMENT_SCAM
REFUND_SCAM
FRAUD_NETWORK
```

## Dashboard

``` http
GET /api/v1/dashboard/summary
GET /api/v1/dashboard/transactions
GET /api/v1/dashboard/clusters
```

## Recipient graph

``` http
GET /api/v1/recipients/{recipient_id}/graph
```

The current frozen contract returns recipient/network intelligence and
aggregate graph evidence.

## Transaction statuses

``` text
PENDING
ALLOWED
CANCELLED
HELD
```

## Friction actions

``` text
ALLOW
VERIFY
STRONG_VERIFY
HOLD
```

## Risk levels

``` text
LOW
MEDIUM
HIGH
CRITICAL
```

Ranges:

``` text
0–30    LOW
31–60   MEDIUM
61–80   HIGH
81–100  CRITICAL
```

## Risk formula

``` text
risk =
    behavior_score * 0.35
  + recipient_score * 0.25
  + intent_score * 0.40
```

## Behavior result

``` json
{
  "score": 87,
  "signals": [
    "AMOUNT_ABOVE_NORMAL",
    "UNUSUAL_TIME",
    "NEW_BEHAVIOR_PATTERN"
  ],
  "features": {},
  "model_version": "behavior-v1"
}
```

## Recipient result

``` json
{
  "score": 76,
  "signals": [
    "NEW_RECIPIENT",
    "HIGH_SENDER_COUNT",
    "SUSPICIOUS_NETWORK"
  ],
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
```

## Intent result

``` json
{
  "category": "BANK_IMPERSONATION",
  "score": 94,
  "signals": [
    "AUTHORITY_IMPERSONATION",
    "ACCOUNT_BLOCK_THREAT",
    "URGENT_TRANSFER"
  ],
  "attributes": {
    "urgency": 0.94,
    "authority_impersonation": 0.97,
    "coercion": 0.82
  },
  "provider": "mock",
  "model_version": "intent-v1"
}
```

## Risk result

``` json
{
  "score": 91,
  "level": "CRITICAL",
  "signals": [
    "AMOUNT_ABOVE_NORMAL",
    "NEW_RECIPIENT",
    "AUTHORITY_IMPERSONATION"
  ],
  "action_recommendation": "HOLD",
  "engine_version": "risk-v1"
}
```

## Friction result

``` json
{
  "action": "HOLD",
  "title": "Payment Paused",
  "message": "This payment may involve a scam or manipulation attempt."
}
```

## Error result

``` json
{
  "error": {
    "code": "RECIPIENT_NOT_FOUND",
    "message": "Recipient does not exist.",
    "request_id": "REQ123"
  }
}
```

Important implementation rule:

> The frontend renders returned risk and friction decisions. It does not
> independently calculate authoritative risk.
