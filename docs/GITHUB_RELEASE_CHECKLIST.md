# GitHub Release Checklist

## 1. Repository cleanliness

Run:

``` powershell
git status --short
git diff --check
```

Do not commit generated artifacts.

Verify that these remain ignored:

``` text
.env
.env.local
node_modules/
.next/
.venv/
__pycache__/
*.db
*.sqlite
*.sqlite3
*.tsbuildinfo
```

## 2. Tests

Backend:

``` powershell
cd apps/api
pytest -q
cd ../..
```

Frontend:

``` powershell
cd apps/web
npm run lint
npm run build
cd ../..
```

## 3. Manual smoke test

Check:

``` text
Landing
Customer Dashboard
Send Money
Transactions
Safety Center
Demo Scenarios
Bank Dashboard
Fraud Graph
```

Critical path:

``` text
U001
→ R020
→ ₹50,000
→ bank officer reason
→ BANK_IMPERSONATION
→ CRITICAL
→ HOLD
→ HELD
```

## 4. Git workflow

Preferred:

``` text
feature branch
      ↓
Pull Request
      ↓
integration
      ↓
CI
      ↓
main
```

Do not directly push feature work to protected `main`.

Use small, meaningful commits.

Suggested commit types:

``` text
feat:
fix:
test:
docs:
chore:
```

## 5. Release tag

After the final release is merged:

``` powershell
git tag -a v0.1.0-hackathon -m "RAKSHA hackathon release"
git push origin v0.1.0-hackathon
```

## 6. GitHub release

Suggested title:

``` text
RAKSHA v0.1.0 — Hackathon Release
```

Suggested summary:

``` text
RAKSHA is a financial safety layer that detects when a legitimate customer
may be manipulated into making a fraudulent payment.

This release contains the integrated customer experience, intelligence
pipeline, bank dashboard, deterministic demo scenarios, recipient-network
analysis, risk engine, adaptive friction, and synthetic data environment.
```

## 7. README order

Keep the README order:

1.  Product name
2.  Value proposition
3.  Core insight
4.  Killer demo
5.  Architecture
6.  Technology
7.  Setup
8.  API
9.  Screenshots
10. Limitations

Do not put a long team implementation diary before the product
explanation.

## 8. Screenshots

Recommended five:

``` text
01 Landing
02 Send Money
03 Payment Paused / CRITICAL
04 Bank Dashboard
05 Fraud Graph
```

Use only synthetic information.

## 9. Repository description

> A financial safety layer that detects when legitimate customers are
> being manipulated into making fraudulent payments using behavior,
> recipient, intent, risk, and adaptive friction intelligence.

## 10. Repository topics

``` text
fintech
fraud-detection
ai
machine-learning
cybersecurity
fastapi
nextjs
python
postgresql
scikit-learn
networkx
hackathon
```

## 11. Final portfolio framing

Prefer:

> **A financial safety layer for authorized payments.**

over:

> A fraud detection project.

The differentiator is:

``` text
Traditional:
Does the transaction look fraudulent?

RAKSHA:
Is the customer being manipulated into making it?
```
