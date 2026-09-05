# RAKSHA Architecture

## Overview

RAKSHA is a modular monolith.

``` text
Customer Web App
       |
       | REST / JSON
       v
FastAPI API
       |
       +-------------------+-------------------+
       |                   |                   |
       v                   v                   v
Behavior             Recipient              Intent
Engine               Engine                 Engine
       |                   |                   |
       +-------------------+-------------------+
                           |
                           v
                      Risk Engine
                           |
                           v
                   Adaptive Friction
                           |
                +----------+----------+
                |          |          |
              ALLOW      VERIFY      HOLD
                                      |
                                      v
                              Bank Dashboard
                                      |
                                      v
                                Fraud Graph
```

## Responsibility boundaries

### API

Handles:

-   HTTP routing
-   validation
-   serialization
-   dependency injection
-   errors

### Behavior

Produces customer-behavior evidence.

### Recipient

Produces recipient and network evidence.

### Intent

Produces payment-intent evidence.

### Risk

Produces authoritative risk assessment.

### Friction

Produces authoritative intervention.

### Frontend

Presents decisions and collects user input.

### PostgreSQL

Stores authoritative durable state.

### Redis

Supporting cache/infrastructure only.

## Transaction data flow

``` text
TransactionContext
      |
      +--> BehaviorResult
      |
      +--> RecipientResult
      |
      +--> IntentResult
               |
               v
         RiskAssessment
               |
               v
        FrictionDecision
               |
               v
          PostgreSQL
               |
               v
           Frontend
```

## Fraud graph

The backend builds a NetworkX graph from transaction relationships.

Example:

``` text
U011 ──┐
U012 ──┤
U013 ──┼── R020
U014 ──┘
```

Current RecipientResult network information includes aggregate values
such as:

``` text
cluster_id
connected_suspicious_users
network_size
```

The frozen contract does not define an arbitrary raw node/edge response,
so the frontend graph should be understood as a constrained presentation
layer rather than a general graph explorer.

## Database relationship

Conceptually:

``` text
User
 ├── Account
 └── Transaction
       ├── IntentResult
       ├── RiskAssessment
       ├── FrictionDecision
       └── AuditEvent

Recipient
 ├── Transaction
 ├── FraudFlag
 └── FraudCluster

ScenarioDefinition
```

## Decision separation

The most important architectural rule is:

``` text
Evidence
   ↓
Risk
   ↓
Intervention
```

No intelligence engine should independently decide `ALLOW` or `HOLD`.

## Error model

Errors use:

``` json
{
  "error": {
    "code": "RECIPIENT_NOT_FOUND",
    "message": "Recipient does not exist.",
    "request_id": "REQ123"
  }
}
```

## Deployment concept

``` text
Browser
   |
   v
Frontend hosting
   |
   v
FastAPI
   |
   +--> Managed PostgreSQL
   |
   +--> Managed Redis
```

The current verified environment is local development.
