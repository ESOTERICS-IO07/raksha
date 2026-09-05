# Security and Limitations

## Prototype status

RAKSHA is a hackathon/prototype banking safety system.

It is not a production banking security platform.

## Synthetic data

The project uses deterministic synthetic data.

Do not add:

-   real customer records
-   real account numbers
-   passwords
-   PINs
-   OTPs
-   CVVs
-   bank credentials
-   identity documents
-   production tokens
-   production API keys

## Secrets

Never commit:

``` text
.env
.env.local
API keys
credentials
private keys
tokens
```

Generated/local artifacts should remain ignored:

``` text
node_modules/
.next/
.venv/
__pycache__/
*.db
*.sqlite
*.sqlite3
*.tsbuildinfo
coverage/
.pytest_cache/
.mypy_cache/
.ruff_cache/
```

## LLM

Intent uses:

``` text
IntentProvider
├── LLMProvider
└── MockIntentProvider
```

The mock provider is important for deterministic demos and provider
fallback.

Do not send real PII to an LLM provider.

## Risk interpretation

Risk scores are prototype outputs.

They are not calibrated probabilities of fraud.

Behavior, recipient, and intent components can all have false positives
or false negatives.

## Recipient graph

The current frozen RecipientResult contract provides aggregate network
evidence:

``` text
cluster_id
connected_suspicious_users
network_size
```

It does not define a general raw node/edge API.

Therefore the current graph UI should not be described as a
production-grade graph investigation platform.

## API security

A production system would additionally require:

-   authentication
-   authorization
-   rate limiting
-   secure secret management
-   HTTPS
-   monitoring
-   abuse prevention
-   dependency/image scanning
-   structured audit logging
-   backup and recovery
-   incident response

These are outside the verified hackathon prototype.

## Database

PostgreSQL is authoritative.

Redis is not authoritative.

Local development credentials are suitable only for local synthetic
development.

## Audit events

The prototype includes an append-only audit-event concept:

``` text
event_id
transaction_id
event_type
timestamp
metadata
```

Production audit storage would require stronger integrity and access
controls.

## Deployment

The verified environment is local development.

A production deployment must separately verify:

-   hosting
-   database networking
-   Redis networking
-   environment variables
-   CORS
-   HTTPS
-   authentication
-   migrations
-   backups
-   observability

## Responsible presentation

Avoid:

> "RAKSHA guarantees fraud detection."

Prefer:

> "RAKSHA combines behavioral, recipient, and intent evidence to
> identify transactions where a customer may be manipulated and applies
> adaptive intervention."
