# RAKSHA Demo Guide

## Objective

Demonstrate one idea:

> **A payment can be authenticated while the customer making it is being
> manipulated.**

## Startup

### Infrastructure

``` powershell
docker compose up -d
```

### Backend

``` powershell
.\apps\api\.venv\Scripts\Activate.ps1
uvicorn app.main:app --reload --app-dir apps/api
```

### Frontend

``` powershell
cd apps/web
npm run dev
```

Open:

``` text
http://localhost:3000
```

## Pre-demo

Check:

``` powershell
Invoke-RestMethod "http://127.0.0.1:8000/health"
Invoke-RestMethod "http://127.0.0.1:8000/api/v1/scenarios"
```

The scenario endpoint should return the eight deterministic scenarios.

## Recommended demo

### 1. Landing

Say:

> "Traditional fraud detection asks whether a transaction looks
> fraudulent. RAKSHA asks whether the customer is being manipulated into
> making it."

### 2. Send money

Use:

``` text
Recipient: R020
Amount: ₹50,000
Reason: Bank officer told me to verify my account
```

### 3. Show the decision

Expected:

``` text
Intent → BANK_IMPERSONATION
Risk → CRITICAL
Action → HOLD
Status → HELD
```

### 4. Explain the evidence

``` text
Behavior:
The payment is unusual.

Recipient:
The recipient has suspicious evidence.

Intent:
The reason contains bank impersonation and urgency signals.

Risk:
The evidence combines into CRITICAL risk.

Friction:
RAKSHA pauses the payment.
```

### 5. Bank dashboard

Show:

-   flagged transaction
-   risk score
-   evidence
-   recipient information
-   intent
-   network context

### 6. Optional normal contrast

``` text
Normal payment
→ LOW
→ ALLOW
```

versus:

``` text
Manipulated payment
→ CRITICAL
→ HOLD
```

## 90-second script

> "This is RAKSHA, a financial safety layer for authorized payments.
>
> Most fraud systems ask whether a transaction looks fraudulent. We ask
> whether the customer is being manipulated.
>
> Here, a customer is trying to send ₹50,000 to a new recipient. The
> reason says that a bank officer told them to verify their account.
>
> RAKSHA combines behavior, recipient, and intent intelligence instead
> of relying on one signal.
>
> The behavior is unusual, the recipient has suspicious evidence, and
> the intent is classified as bank impersonation.
>
> The combined risk becomes critical, so adaptive friction pauses the
> payment.
>
> The important point is that the transaction was authenticated. The
> customer was still at risk because they were being manipulated."

## Backup API demo

``` powershell
$body = @{
    user_id = "U001"
    recipient_id = "R020"
    amount = 50000
    currency = "INR"
    reason = "Bank officer told me to verify my account"
} | ConvertTo-Json

Invoke-RestMethod `
  -Uri "http://127.0.0.1:8000/api/v1/transactions/analyze" `
  -Method POST `
  -ContentType "application/json" `
  -Body $body | ConvertTo-Json -Depth 10
```

Look for:

``` text
BANK_IMPERSONATION
CRITICAL
HOLD
```

## Fast troubleshooting

### Demo cards missing

``` powershell
Invoke-RestMethod "http://127.0.0.1:8000/api/v1/scenarios"
```

If empty:

``` powershell
python scripts/seed_db.py
```

### Failed to fetch

Check:

-   backend is running
-   port 8000 is available
-   frontend is running on port 3000
-   local CORS is configured

### INVALID_ID_FORMAT

Use the public demo IDs:

``` text
U001
R020
```

and verify the integrated public-ID translation is present.

### Python import errors

Verify:

``` powershell
python -c "import sys; print(sys.executable)"
```

It must point to:

``` text
apps/api/.venv/
```

Then:

``` powershell
python -m pip install -r apps/api/requirements.txt
```

## Demo rule

Do not add new features immediately before the presentation.

Prioritize:

``` text
Reliability
>
Reproducibility
>
Clear story
>
Visual polish
>
New features
```
