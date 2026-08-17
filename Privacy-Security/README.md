# Privacy & Security

## Overview

The **Privacy & Security module** protects organizations participating in the Federated Learning system. It ensures that private training data stays within each organization while model updates are protected before aggregation.

### Main Responsibilities

* 🔐 **Authentication & Authorization** — JWT + RBAC for secure API access.
* 🛡️ **Secure Aggregation** — hides individual organizations' model updates from the central server.
* 🔒 **Differential Privacy** — clips model updates and adds calibrated noise to reduce information leakage.
* 📊 **Privacy Budget** — tracks `ε` (epsilon) and `δ` (delta) across training rounds.
* 🚫 **Input Validation** — validates participants, model versions, updates, and training rounds.
* 📝 **Audit Logging** — records security, privacy, training, and aggregation events.
* 🔄 **Dropout Handling** — safely handles participants that disconnect during a round.

## Privacy Flow

```text
Private Data
     ↓
Local Training
     ↓
Model Update
     ↓
Validation
     ↓
Update Clipping
     ↓
Secure Aggregation
     ↓
Differential Privacy
     ↓
Protected Update
     ↓
Flower Server
     ↓
Global Model
```

## Secure Aggregation

Instead of allowing the server to see:

```text
Org A Update
Org B Update
Org C Update
```

the system protects individual updates so that the server primarily obtains:

```text
Aggregate(Update A + Update B + Update C)
```

without exposing each organization's contribution.

## Differential Privacy

The update is clipped and noise is added:

```text
Model Update
     ↓
Clip
     ↓
Add DP Noise
     ↓
Protected Update
```

Key parameters:

```text
ε (epsilon) → privacy level
δ (delta)   → failure probability
```

Smaller `ε` generally provides stronger privacy but can reduce model utility.

## Security Stack

```text
FastAPI
   │
   ├── JWT Authentication
   ├── RBAC
   ├── Input Validation
   └── Security APIs
        │
        ├── PostgreSQL → Users, privacy budgets, audit logs
        └── Redis      → Round/session state
```

## Expected Output

The module provides:

* Protected model updates
* Secure aggregation
* Differential privacy
* Privacy-budget tracking
* Authentication and authorization
* Security/audit logs
* Privacy and training metrics

## Technology

**FastAPI · Flower · PostgreSQL · Redis · JWT · RBAC · Differential Privacy · Pytest**

### Core Principle

> **Raw organizational training data never leaves the organization. Only privacy-protected model information participates in federated learning.**
