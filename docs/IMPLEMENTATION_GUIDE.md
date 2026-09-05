# RAKSHA Implementation Guide

## 1. Build order

The project was intentionally implemented in layers:

``` text
FastAPI foundation
        ↓
PostgreSQL + SQLAlchemy
        ↓
Alembic
        ↓
Shared Pydantic contracts
        ↓
API foundation
        ↓
Behavior adapter
Recipient adapter
Intent provider
        ↓
Risk
        ↓
Adaptive Friction
        ↓
Persistence
        ↓
Synthetic data
        ↓
Scenario simulator
        ↓
Next.js frontend
        ↓
Integration QA
        ↓
Demo hardening
```

This order prevents individual frontend or intelligence implementations
from silently inventing incompatible interfaces.

## 2. Backend structure

Backend root:

``` text
apps/api/app/
```

Important areas:

``` text
api/v1/       HTTP routes
core/         configuration
models/       SQLAlchemy models
schemas/      canonical Pydantic schemas
services/     intelligence and decision services
graph/        fraud-network utilities
db/           database session/base
main.py       FastAPI application
```

## 3. Database

The main tables are:

``` text
users
accounts
recipients
transactions
transaction_signals
behavior_profiles
intent_results
risk_assessments
friction_decisions
fraud_flags
fraud_clusters
scenario_definitions
audit_events
```

Apply migrations:

``` powershell
cd apps/api
alembic upgrade head
```

PostgreSQL is authoritative.

## 4. Behavior Intelligence

Purpose:

> Determine whether the current transaction is unusual for the customer.

The result contains:

``` text
score
signals
features
model_version
```

The score is 0--100.

The engine uses behavioral rules and Isolation Forest anomaly analysis.

It does not decide the final action.

## 5. Recipient Intelligence

Purpose:

> Determine whether the recipient has suspicious history or network
> evidence.

Signals can include:

``` text
NEW_RECIPIENT
HIGH_SENDER_COUNT
PREVIOUS_FLAGS
SUSPICIOUS_HISTORY
SUSPICIOUS_NETWORK
```

Network analysis uses NetworkX.

The platform adapter translates database transaction fields:

``` text
user_id      → sender
recipient_id → recipient
```

for the engine's graph interface.

## 6. Intent Intelligence

Purpose:

> Determine why the customer is making the payment.

Provider abstraction:

``` text
IntentProvider
    ├── LLMProvider
    └── MockIntentProvider
```

Supported categories:

``` text
NORMAL
PERSONAL_TRANSFER
PURCHASE
BILL_PAYMENT
BANK_IMPERSONATION
ACCOUNT_SUSPENSION
KYC_SCAM
INVESTMENT_SCAM
REFUND_SCAM
TECH_SUPPORT_SCAM
OTP_SCAM
REMOTE_ACCESS_SCAM
UNKNOWN
```

## 7. Risk

Inputs:

``` text
TransactionContext
BehaviorResult
RecipientResult
IntentResult
```

Formula:

``` text
behavior × 0.35
+ recipient × 0.25
+ intent × 0.40
```

Risk level is then mapped to adaptive friction.

High-confidence rules can escalate risk. Example:

``` text
BANK_IMPERSONATION
+
high-value transaction
+
new recipient
=
CRITICAL
```

## 8. Adaptive Friction

``` text
LOW       → ALLOW
MEDIUM    → VERIFY
HIGH      → STRONG_VERIFY
CRITICAL  → HOLD
```

The frontend renders the returned action and does not calculate the
authoritative action itself.

## 9. Persistence

An analyzed transaction persists:

``` text
Transaction
IntentResult
RiskAssessment
FrictionDecision
```

The dashboard reads persisted risk information.

## 10. Scenario system

Scenario definitions are stored in `scenario_definitions`.

The seed script inserts eight deterministic scenarios.

The scenario runner:

1.  loads a scenario
2.  creates deterministic transaction input
3.  routes it through the existing transaction intelligence pipeline
4.  returns the pipeline result
5.  persists the transaction and intelligence outputs

The runner must not simply hardcode a fake final risk result.

## 11. Public identifiers

Demo-facing IDs are readable:

``` text
U001
R020
```

Database foreign keys are numeric.

The platform layer translates public IDs into internal numeric
identifiers while preserving the external API contract.

## 12. Frontend

Frontend root:

``` text
apps/web/
```

The frontend is responsible for:

-   user input
-   transaction presentation
-   risk presentation
-   friction presentation
-   dashboards
-   accessibility
-   demo scenario interaction

It is not the authoritative decision engine.

## 13. Local CORS

Local development uses:

``` text
http://localhost:3000
http://127.0.0.1:8000
```

The backend permits the frontend origin through CORS.

## 14. Testing

Backend:

``` powershell
cd apps/api
pytest -q
```

Frontend:

``` powershell
cd apps/web
npm run lint
npm run build
```

The integrated backend baseline reached 78 passing tests.

## 15. Engineering rules

Do not:

-   change shared contracts silently
-   calculate authoritative risk in the frontend
-   let individual engines decide ALLOW/HOLD
-   use Redis as the source of truth
-   commit secrets
-   commit generated dependencies
-   introduce real banking data

When a dependency is unavailable during development, use a mock that
conforms exactly to the existing contract.
