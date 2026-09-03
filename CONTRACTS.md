# RAKSHA — Master Engineering Contract

**Version:** 1.0.0  
**Status:** FROZEN — Hackathon Implementation Contract  
**Project:** RAKSHA — Intent-Aware Financial Safety Layer  
**Primary Problem:** Protecting Vulnerable Customers from Digital Financial Fraud  
**Team Size:** 5  
**Target Build Window:** 24–36 hours  
**Architecture:** Modular Monolith

---

## 0. Contract Authority

This document is the single source of truth for implementation decisions during the hackathon.

If a teammate is unsure about a behavior, schema, endpoint, directory, ownership boundary, or integration rule, this contract takes precedence over personal assumptions.

If a required behavior is not specified here, the team must document the decision in a PR before implementation. No silent assumptions.

### Frozen Core Principle

> RAKSHA does not directly ask only whether a transaction is fraudulent. It evaluates whether the transaction is normal for the customer, whether the recipient presents risk, and whether the customer may be being socially engineered. The Risk Engine combines these signals. Adaptive Friction converts the risk assessment into ALLOW, VERIFY, STRONG_VERIFY, or HOLD.

---

# 1. Product Definition

## 1.1 Product

RAKSHA is a prototype financial-safety layer positioned before payment authorization.

It analyzes a payment request using three independent intelligence engines:

1. Behavior Engine — customer-specific behavioral anomaly.
2. Recipient Engine — recipient trust and network risk.
3. Intent Engine — social-engineering/scam intent.

These outputs are combined by the Risk Engine. The Adaptive Friction Engine decides the appropriate intervention.

## 1.2 Demo Scope

The prototype is a simulation. It MUST NOT connect to real banking accounts, real UPI payment rails, real customer credentials, real OTPs, or real financial accounts.

The demo must support:

- Normal payment.
- Suspicious/unusual payment.
- Social-engineering payment.
- Payment intervention.
- Explanation of why a payment was flagged.
- Bank-side investigation dashboard.
- Fraud relationship graph.
- Accessibility/voice presentation.
- Deterministic seeded scenarios.

## 1.3 Novelty Statement

> Traditional fraud detection asks whether a transaction looks fraudulent. RAKSHA asks whether the customer is being manipulated into making it.

The differentiating combination is:

**Behavior Context + Recipient Intelligence + Intent Intelligence + Adaptive Friction.**

---

# 2. Technology Stack — FROZEN

| Layer | Technology |
|---|---|
| Frontend | Next.js + TypeScript |
| UI | Tailwind CSS + shadcn/ui |
| Icons | Lucide |
| API state | TanStack Query |
| Backend | FastAPI + Python |
| Validation | Pydantic |
| Database | PostgreSQL |
| ORM | SQLAlchemy 2.x |
| Migrations | Alembic |
| Cache | Redis |
| Behavior ML | scikit-learn / Isolation Forest |
| Recipient Analysis | Python + PostgreSQL |
| Fraud Graph | NetworkX |
| Graph UI | React Flow |
| Intent AI | LLM API through provider abstraction |
| Accessibility | Web Speech API + accessible UI |
| Charts | Recharts |
| Backend tests | pytest |
| Frontend tests | Vitest + Playwright |
| Python quality | Ruff + Black + mypy |
| JS quality | ESLint + Prettier |
| API | REST + JSON |
| API docs | OpenAPI / Swagger |
| Data | Synthetic deterministic dataset |
| CI | GitHub Actions |
| Frontend deployment | Vercel |
| Backend deployment | Render/Railway/Fly.io |
| Managed DB | PostgreSQL provider such as Neon |
| Redis | Managed Redis provider such as Upstash |

## Explicitly excluded from MVP

- Blockchain
- AR/VR
- Kubernetes
- Kafka
- Microservices
- Custom LLM training
- Real banking/UPI integration
- Production authentication
- Real customer data

---

# 3. Architecture

```text
Customer Web App
      |
      | REST/JSON
      v
FastAPI API Layer
      |
      +-------------------+-------------------+
      |                   |                   |
      v                   v                   v
Behavior Engine      Recipient Engine      Intent Engine
      |                   |                   |
      +-------------------+-------------------+
                          |
                          v
                    Risk Engine
                          |
                          v
                 Adaptive Friction
                          |
              +-----------+-----------+
              |           |           |
            ALLOW       VERIFY       HOLD
                                      |
                                      v
                               Bank Dashboard
                                      |
                                      v
                                Fraud Graph
```

### Mandatory responsibility separation

- Engines produce evidence.
- Risk Engine produces the final risk assessment.
- Adaptive Friction produces the final user-facing action.
- Frontend renders decisions; it MUST NOT independently calculate authoritative risk.
- Database is the source of truth.
- Redis is not the source of truth.

---

# 4. Repository Structure

```text
raksha/
├── apps/
│   ├── web/
│   │   ├── app/
│   │   │   ├── customer/
│   │   │   ├── bank/
│   │   │   ├── demo/
│   │   │   └── api-client/
│   │   ├── components/
│   │   │   ├── transaction/
│   │   │   ├── risk/
│   │   │   ├── accessibility/
│   │   │   ├── dashboard/
│   │   │   └── graph/
│   │   ├── lib/
│   │   ├── hooks/
│   │   ├── types/
│   │   └── tests/
│   │
│   └── api/
│       ├── app/
│       │   ├── api/
│       │   │   └── v1/
│       │   │       ├── transactions.py
│       │   │       ├── users.py
│       │   │       ├── recipients.py
│       │   │       ├── scenarios.py
│       │   │       └── dashboard.py
│       │   ├── core/
│       │   ├── models/
│       │   ├── schemas/
│       │   ├── services/
│       │   │   ├── behavior/
│       │   │   ├── recipient/
│       │   │   ├── intent/
│       │   │   ├── risk/
│       │   │   └── friction/
│       │   ├── graph/
│       │   ├── db/
│       │   └── main.py
│       └── tests/
│
├── packages/
│   └── contracts/
│       ├── openapi/
│       ├── schemas/
│       └── README.md
│
├── data/
│   ├── seed/
│   ├── scenarios/
│   └── generated/
│
├── scripts/
│   ├── seed_db.py
│   ├── generate_data.py
│   └── reset_demo.py
│
├── docs/
│   ├── architecture/
│   ├── demo/
│   └── decisions/
│
├── .github/
│   └── workflows/
│       └── ci.yml
│
├── .env.example
├── docker-compose.yml
├── README.md
├── CONTRACTS.md
├── pyproject.toml
└── package.json
```

Directory ownership is logical, not permission-based. Integration changes may touch multiple areas only when required and documented.

---

# 5. Five-Person Ownership

## Person 1 — Customer Experience

Owns:

- Customer transaction flow.
- Risk/intervention screens.
- Accessibility mode.
- Voice presentation.
- Customer-side components.

Primary directories:

```text
apps/web/app/customer/
apps/web/components/transaction/
apps/web/components/risk/
apps/web/components/accessibility/
```

Must not implement authoritative risk scoring.

---

## Person 2 — Behavior Intelligence

Owns:

- Transaction feature extraction.
- Baseline behavior calculation.
- Isolation Forest.
- Behavioral rules.
- Behavior result schema.
- Behavior tests.

Primary directory:

```text
apps/api/app/services/behavior/
```

Output:

```json
{
  "score": 0,
  "signals": [],
  "features": {}
}
```

Score range: 0–100.

---

## Person 3 — Recipient Intelligence

Owns:

- Recipient analysis.
- Recipient risk score.
- Recipient history queries.
- Fraud graph construction.
- NetworkX analysis.
- Graph API data.
- Recipient tests.

Primary directories:

```text
apps/api/app/services/recipient/
apps/api/app/graph/
apps/web/components/graph/
```

Score range: 0–100.

---

## Person 4 — Intent + Risk

Owns:

- Intent provider abstraction.
- LLM integration.
- Intent classification.
- Intent score.
- Risk aggregation.
- Risk rules.
- Adaptive Friction policy.
- Risk/friction tests.

Primary directories:

```text
apps/api/app/services/intent/
apps/api/app/services/risk/
apps/api/app/services/friction/
```

---

## Person 5 — Platform + Integration

Owns:

- FastAPI foundation.
- PostgreSQL.
- SQLAlchemy models.
- Alembic.
- API contracts.
- Seed data.
- Scenario simulator backend.
- CI.
- Deployment.
- Integration testing.
- Release coordination.

Primary directories:

```text
apps/api/app/api/
apps/api/app/models/
apps/api/app/schemas/
apps/api/app/db/
data/
scripts/
.github/
```

Person 5 is integration owner, not the only person responsible for fixing everyone else's code.

---

# 6. Git Workflow

## Main branches

```text
main
integration
```

Feature branches:

```text
feature/<area>-<short-name>
```

Examples:

```text
feature/behavior-engine
feature/recipient-engine
feature/intent-engine
feature/risk-engine
feature/customer-flow
feature/bank-dashboard
```

## ABSOLUTE RULE

```text
NEVER:
git push origin main
```

Flow:

```text
feature branch
      |
      v
push
      |
      v
Pull Request
      |
      v
integration
      |
      v
CI + manual test
      |
      v
main
```

No direct pushes to `main`.

No direct pushes to `integration` unless the team explicitly agrees during emergency integration.

---

# 7. Commit Convention

Use:

```text
feat: add behavior scoring
feat: add recipient graph
feat: add intent classifier
feat: add transaction intervention UI

fix: correct risk threshold
fix: handle missing recipient

test: add risk engine tests
docs: update API contract
chore: configure CI
```

Commits should be small enough to understand.

Do not use:

```text
final
final2
final_final
final_really_final
```

---

# 8. Pull Request Contract

Every PR MUST contain:

1. What changed.
2. Why it changed.
3. Files/areas affected.
4. API/schema changes, if any.
5. Tests performed.
6. Screenshots/video for UI changes.
7. Any contract change.
8. Any known limitation.

PR title:

```text
<type>: <short description>
```

Example:

```text
feat: implement behavior anomaly scoring
```

---

# 9. Shared Data Contract

All engines receive the normalized transaction context.

```json
{
  "transaction_id": "TX1001",
  "user_id": "U001",
  "recipient_id": "R014",
  "amount": 50000,
  "currency": "INR",
  "timestamp": "2026-09-03T23:43:00+05:30",
  "device_id": "D001",
  "location": {
    "country": "IN",
    "region": "TN"
  },
  "reason": "Bank officer told me to verify my account"
}
```

The `reason` field is optional for ordinary payment simulation but required for Intent Engine scenarios.

---

# 10. Behavior Engine Contract

## Input

```text
TransactionContext
+
CustomerBehaviorProfile
```

## Output

```json
{
  "score": 87,
  "signals": [
    "AMOUNT_ABOVE_NORMAL",
    "UNUSUAL_TIME",
    "NEW_BEHAVIOR_PATTERN"
  ],
  "features": {
    "amount_deviation": 4.8,
    "hour_deviation": 2.1,
    "recipient_frequency": 0
  },
  "model_version": "behavior-v1"
}
```

## Rules

- Score must be integer 0–100.
- Signals must be machine-readable enum strings.
- No free-form prose is consumed by Risk Engine.
- Behavior Engine must not decide ALLOW/HOLD.

---

# 11. Recipient Engine Contract

## Output

```json
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

Recipient analysis MUST be based only on synthetic/demo data.

---

# 12. Intent Engine Contract

## Provider abstraction

```text
IntentProvider
  ├── LLMProvider
  └── MockIntentProvider
```

Mock provider is mandatory for demo fallback.

## Output

```json
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

Allowed categories:

```text
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

LLM output MUST be validated against the schema.

---

# 13. Risk Engine Contract

Risk Engine input:

```text
TransactionContext
BehaviorResult
RecipientResult
IntentResult
```

Initial weighting:

```text
Behavior   = 35%
Recipient  = 25%
Intent     = 40%
```

Base score:

```text
risk =
    behavior_score * 0.35
  + recipient_score * 0.25
  + intent_score * 0.40
```

Round to integer.

## Escalation rules

Deterministic high-confidence signals may override the base score.

Example:

```text
IF bank impersonation
AND high-value transaction
AND new recipient
THEN risk level = CRITICAL
```

The exact threshold values must be centralized in configuration, not scattered across modules.

## Risk levels

```text
0–30   LOW
31–60  MEDIUM
61–80  HIGH
81–100 CRITICAL
```

## Output

```json
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

---

# 14. Adaptive Friction Contract

Adaptive Friction converts Risk Assessment into action.

## Default policy

```text
LOW
→ ALLOW

MEDIUM
→ VERIFY

HIGH
→ STRONG_VERIFY

CRITICAL
→ HOLD
```

Possible actions:

```text
ALLOW
VERIFY
STRONG_VERIFY
HOLD
```

The frontend must render the returned action.

The frontend must not independently reinterpret the score.

## Example

```text
Risk 18 → ALLOW
Risk 48 → VERIFY
Risk 72 → STRONG_VERIFY
Risk 94 → HOLD
```

High-confidence safety rules may force HOLD regardless of base score.

---

# 15. Core API

Base path:

```text
/api/v1
```

## Analyze transaction

```http
POST /transactions/analyze
```

Request:

```json
{
  "user_id": "U001",
  "recipient_id": "R014",
  "amount": 50000,
  "currency": "INR",
  "reason": "Bank officer told me to verify my account"
}
```

Response:

```json
{
  "transaction_id": "TX1001",
  "behavior": {},
  "recipient": {},
  "intent": {},
  "risk": {
    "score": 94,
    "level": "CRITICAL"
  },
  "friction": {
    "action": "HOLD",
    "title": "Payment Paused",
    "message": "This payment resembles an account-verification scam."
  }
}
```

## Scenarios

```http
GET /scenarios
GET /scenarios/{scenario_id}
POST /scenarios/{scenario_id}/run
```

## Dashboard

```http
GET /dashboard/summary
GET /dashboard/transactions
GET /dashboard/clusters
```

## Graph

```http
GET /recipients/{recipient_id}/graph
```

Exact request/response schemas MUST live in the shared contract package/OpenAPI definition.

---

# 16. Database Model

Minimum tables:

```text
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

## Transaction

Required fields:

```text
id
user_id
recipient_id
amount
currency
timestamp
device_id
reason
status
created_at
```

Status:

```text
PENDING
ALLOWED
CANCELLED
HELD
```

## Audit Event

Must record:

```text
event_id
transaction_id
event_type
timestamp
metadata
```

Audit events should be append-only during the prototype.

---

# 17. Error Contract

All API errors use:

```json
{
  "error": {
    "code": "RECIPIENT_NOT_FOUND",
    "message": "Recipient does not exist.",
    "request_id": "REQ123"
  }
}
```

No engine may crash the entire transaction-analysis pipeline because an optional signal is unavailable.

If an intelligence provider fails:

```text
Intent API unavailable
        ↓
Mock/fallback provider
        ↓
continue analysis
```

If a critical engine fails and no safe fallback exists, the system must fail safely according to the configured demo policy rather than silently marking a transaction safe.

---

# 18. Synthetic Data Contract

No real PII.

Seed data must contain:

### Users

At least:

```text
10–30 demo users
```

### Recipients

At least:

```text
20–50 recipients
```

### Transactions

At least:

```text
200+ synthetic transactions
```

### Fraud scenarios

Minimum:

```text
NORMAL_PAYMENT
UNUSUAL_PAYMENT
NEW_RECIPIENT
BANK_IMPERSONATION
ACCOUNT_SUSPENSION
INVESTMENT_SCAM
REFUND_SCAM
FRAUD_NETWORK
```

The fraud network scenario must contain multiple customers connected to a common suspicious recipient.

---

# 19. Demo Scenarios

## Scenario A — Normal

```text
Amount: ₹850
Recipient: frequent grocery merchant
Reason: grocery purchase
```

Expected:

```text
LOW
ALLOW
```

## Scenario B — Unusual

```text
Amount: ₹25,000
Recipient: new
Time: unusual
Reason: personal payment
```

Expected:

```text
MEDIUM/HIGH
VERIFY or STRONG_VERIFY
```

## Scenario C — Social Engineering

```text
Amount: ₹50,000
Recipient: new
Reason:
"Bank officer said my account will be blocked
unless I transfer this immediately."
```

Expected:

```text
CRITICAL
HOLD
```

Signals:

```text
AUTHORITY_IMPERSONATION
ACCOUNT_BLOCK_THREAT
URGENT_TRANSFER
NEW_RECIPIENT
AMOUNT_ABOVE_NORMAL
```

## Scenario D — Fraud Network

Multiple users send unusual transactions to the same recipient.

Expected:

```text
SUSPICIOUS_CLUSTER
```

Dashboard must visualize the relationship.

---

# 20. Customer UI Requirements

Customer flow:

```text
Customer Dashboard
      ↓
Send Money
      ↓
Enter Recipient + Amount
      ↓
Optional Reason
      ↓
Analyze
      ↓
Risk/Intervention
      ↓
ALLOW / VERIFY / STRONG_VERIFY / HOLD
```

For HOLD:

Display:

- clear warning.
- reason for intervention.
- suspicious signals in human-readable language.
- cancel option.
- bank contact option in demo.
- trusted-contact option if implemented.

Never expose internal model jargon such as:

```text
Isolation Forest anomaly = 0.872
```

Customer copy must be simple.

---

# 21. Bank Dashboard Requirements

Dashboard must display:

```text
Total analyzed
Allowed
Verified
Held
High-risk count
Critical count
Top scam categories
Recent high-risk transactions
Suspicious recipient clusters
```

Transaction detail must show:

```text
Transaction
Behavior score
Recipient score
Intent score
Final risk
Signals
Action
Timestamp
```

---

# 22. Accessibility Requirements

Minimum:

- Keyboard navigation.
- Semantic labels.
- High-contrast compatible UI.
- Large touch targets.
- Large text mode.
- Simple-language intervention copy.
- Text-to-speech for critical transaction warnings.
- No color-only indication of risk.

Example:

Bad:

```text
RED = dangerous
```

Good:

```text
🔴 CRITICAL — PAYMENT PAUSED
```

The status must be communicated through text as well as visual styling.

---

# 23. Security Rules for Prototype

Never collect or store:

```text
real passwords
real PINs
real OTPs
CVV
bank credentials
real account numbers
real identity documents
```

All customer and transaction data is synthetic.

LLM prompts must not contain real PII.

Environment secrets belong in `.env` and secret-management systems, never Git.

`.env` must be in `.gitignore`.

---

# 24. Testing Acceptance Criteria

Minimum backend tests:

- Behavior score bounds.
- Recipient score bounds.
- Intent schema validation.
- Risk weighting.
- Risk threshold mapping.
- Critical escalation rules.
- Adaptive friction mapping.
- Missing optional fields.
- Provider failure fallback.
- API error format.

Minimum frontend tests:

- Normal payment flow.
- Suspicious payment flow.
- Critical HOLD screen.
- Accessibility warning rendering.

Minimum E2E:

```text
Scenario C:
Start scenario
→ analyze transaction
→ CRITICAL
→ HOLD
→ warning displayed
```

---

# 25. CI Contract

Every PR must pass:

```text
Frontend:
lint
typecheck
tests

Backend:
lint
format check
typecheck
pytest
```

CI failure blocks merge.

If a check cannot be completed because of a hackathon-time constraint, the PR must explicitly document why.

---

# 26. Environment Variables

`.env.example` must define placeholders such as:

```text
DATABASE_URL=
REDIS_URL=
LLM_PROVIDER=
LLM_API_KEY=
NEXT_PUBLIC_API_BASE_URL=
```

No secret values committed.

Provider-specific variables must be documented.

---

# 27. Development Commands

The final repository README must provide commands equivalent to:

```text
# install frontend
npm install

# run frontend
npm run dev

# install backend
pip install -r requirements.txt

# run backend
uvicorn app.main:app --reload

# run tests
pytest
npm test

# seed database
python scripts/seed_db.py
```

Exact commands may be adapted to the chosen package manager, but the README must provide one canonical path.

---

# 28. Integration Order

The team must integrate in this order:

```text
1. Repository + database + API foundation
2. Shared schemas
3. Synthetic dataset
4. Behavior Engine
5. Recipient Engine
6. Intent Engine
7. Risk Engine
8. Adaptive Friction
9. Customer UI
10. Bank Dashboard
11. Fraud Graph
12. Accessibility
13. End-to-end scenarios
14. Deployment
15. Demo hardening
```

Do not wait until hour 30 to discover that the engines disagree on JSON schemas.

---

# 29. Parallel Development Contract

Each person must begin from:

1. Current `integration`.
2. Their assigned feature branch.
3. Shared schemas already merged.

If an interface is not ready, use a mock implementation conforming to the contract.

Example:

```text
Person 1 can build UI
using mocked /transactions/analyze
```

while Person 4 builds the real Risk Engine.

Mocks MUST match the same schema.

---

# 30. Definition of Done

A feature is DONE only when:

- Code is implemented.
- Contract is respected.
- Tests exist for critical behavior.
- No secrets are committed.
- Lint/type checks pass.
- PR is reviewed.
- Feature is integrated into `integration`.
- Relevant demo scenario works.

“Works on my laptop” is not Definition of Done.

---

# 31. Demo Narrative Contract

The demo MUST communicate:

### Problem

A legitimate authenticated customer can still be manipulated into making a fraudulent payment.

### Innovation

RAKSHA evaluates:

```text
ME
+
WHO
+
WHY
```

Meaning:

```text
ME    → Behavior
WHO   → Recipient
WHY   → Intent
```

Then:

```text
Evidence
   ↓
Risk
   ↓
Adaptive Intervention
```

### Demo sequence

```text
Normal
→ Allow

Unusual
→ Verify

Social engineering
→ Hold

Fraud network
→ Investigate
```

The social-engineering scenario is the climax.

---

# 32. Pitch Statement

Primary:

> “RAKSHA doesn't just detect fraudulent transactions. It detects when a legitimate customer is being manipulated into making one.”

Supporting:

> “Behavior asks: Is this normal for me?”

> “Recipient asks: Who am I paying?”

> “Intent asks: Why am I paying?”

> “Our Risk Engine combines these signals, and Adaptive Friction decides how much intervention is necessary.”

---

# 33. Engineering Non-Goals

The team must not spend hackathon time on:

- Real UPI integration.
- Real banking integration.
- Production-grade identity verification.
- Training large ML models.
- Blockchain.
- AR/VR.
- Complex distributed systems.
- Mobile native applications unless explicitly required.
- Feature expansion after the core demo works.

Priority order:

```text
CORE FLOW
>
RELIABILITY
>
DEMO QUALITY
>
ACCESSIBILITY
>
VISUAL POLISH
>
EXTRA FEATURES
```

---

# 34. Final Architecture Principle

The system must preserve this chain:

```text
TRANSACTION
    ↓
BEHAVIOR
    ↓
RECIPIENT
    ↓
INTENT
    ↓
RISK
    ↓
FRICTION
    ↓
ACTION
```

No shortcut is permitted where the frontend invents risk, an engine blocks a transaction independently, or the Intent Engine directly controls payment authorization.

The Risk Engine is the authoritative risk decision layer.

Adaptive Friction is the authoritative intervention layer.

The UI is the presentation layer.

---

# 35. Final Acceptance Test

The project is hackathon-demo ready when this exact flow succeeds:

```text
User selects Social Engineering scenario
        ↓
₹50,000 payment
        ↓
Behavior detects unusual amount/time
        ↓
Recipient detects new/suspicious recipient
        ↓
Intent detects bank impersonation + urgency
        ↓
Risk Engine produces ≥ 81 / CRITICAL
        ↓
Adaptive Friction returns HOLD
        ↓
Customer sees clear warning
        ↓
Payment is not marked ALLOWED
        ↓
Bank dashboard shows the event
        ↓
Fraud graph shows recipient connections
```

If that flow works reliably, the core product works.

Everything else is polish.
