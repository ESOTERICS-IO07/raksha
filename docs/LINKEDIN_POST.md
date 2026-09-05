# LinkedIn Post

## Recommended post

**We built RAKSHA --- a financial safety layer designed to detect when a
legitimate customer may be manipulated into making a fraudulent
payment.**

Traditional fraud detection asks:

> **"Does this transaction look fraudulent?"**

RAKSHA asks:

> **"Is the customer being manipulated into making it?"**

The system combines:

-   Behavior Intelligence --- is this transaction normal?
-   Recipient Intelligence --- who is receiving the money?
-   Intent Intelligence --- why is the customer making the payment?
-   Risk Engine --- how does the evidence combine?
-   Adaptive Friction --- should the payment be allowed, verified, or
    held?

In our demo, a customer attempts to send **₹50,000** to a new recipient
after being told:

> "Bank officer told me to verify my account."

RAKSHA identifies **BANK_IMPERSONATION**, evaluates the transaction as
**CRITICAL**, and applies **HOLD** before the payment leaves.

The interesting part isn't simply detecting a suspicious transaction.

It's recognizing that **a transaction can be authenticated while the
customer is simultaneously being manipulated.**

Built with:

**Next.js · TypeScript · FastAPI · Python · PostgreSQL · SQLAlchemy ·
scikit-learn · NetworkX · LLM provider abstraction**

Built as part of our hackathon project.

GitHub: `<ADD-REPOSITORY-LINK>`

#Hackathon #FinTech #FraudDetection #AI #MachineLearning #CyberSecurity
#Python #NextJS #SoftwareEngineering
