<p align="center">
  <img src="https://img.shields.io/badge/🛡️-Federix-6366f1?style=for-the-badge&labelColor=0f172a" alt="Federix" height="40"/>
</p>

<h1 align="center">Federix</h1>
<h3 align="center">🔒 Multi-Organization Federated Learning with Privacy-Preserving AI</h3>

<p align="center">
  <em>Train a shared global AI model across independent organizations — without any raw data ever leaving its own infrastructure.</em>
  <br />
  Privacy enforced through <strong>Secure Aggregation</strong> and <strong>Differential Privacy</strong>, with full auditability and a production model-serving pipeline.
</p>

<p align="center">
  <img src="https://img.shields.io/badge/FastAPI-Backend-009688?style=flat-square&logo=fastapi&logoColor=white" alt="FastAPI"/>
  <img src="https://img.shields.io/badge/Flower-FL_Orchestration-FF6F61?style=flat-square" alt="Flower"/>
  <img src="https://img.shields.io/badge/PyTorch-Training-EE4C2C?style=flat-square&logo=pytorch&logoColor=white" alt="PyTorch"/>
  <img src="https://img.shields.io/badge/PostgreSQL-Storage-4169E1?style=flat-square&logo=postgresql&logoColor=white" alt="PostgreSQL"/>
  <img src="https://img.shields.io/badge/Redis-Cache-DC382D?style=flat-square&logo=redis&logoColor=white" alt="Redis"/>
  <img src="https://img.shields.io/badge/React-Frontend-61dafb?style=flat-square&logo=react&logoColor=white" alt="React"/>
  <img src="https://img.shields.io/badge/Docker-Deploy-2496ED?style=flat-square&logo=docker&logoColor=white" alt="Docker"/>
  <img src="https://img.shields.io/badge/License-MIT-yellow?style=flat-square" alt="License"/>
</p>

<p align="center">
  <a href="#-overview">Overview</a> •
  <a href="#-architecture">Architecture</a> •
  <a href="#-core-components">Components</a> •
  <a href="#-data-flow">Data Flow</a> •
  <a href="#-tech-stack">Tech Stack</a> •
  <a href="#-getting-started">Getting Started</a> •
  <a href="#-privacy--security">Privacy</a> •
  <a href="#-deployment">Deployment</a>
</p>

---

> 🎯 **Mission:** Enable collaborative AI training across organizational boundaries while guaranteeing that no organization's private data is ever exposed — enforced by cryptographic and statistical privacy mechanisms.

---

## 🌐 Overview

Traditional machine learning requires pooling everyone's data into one place. Federix avoids that entirely using **Federated Learning**: each participating organization trains a copy of a shared model on its own private data, and only the resulting **model updates** (never the raw data) are sent to a central server for aggregation into an improved **Global Model**.

The project is organized around three functional teams, unified by shared **contracts** (interfaces/schemas) so each team can build independently against a stable API:

| Team | Directory | Responsibility |
|------|-----------|---------------|
| **🤖 Team A — AI Core** | `team-a-ai-core/` | Model architecture, local training, Flower-based FL client/server |
| **🔐 Team B — Privacy & Security** | `team-b-privacy-security/` | Secure Aggregation, Differential Privacy, encryption, credentials |
| **🖥️ Team C — Platform** | `team-c-platform/` | FastAPI backend, frontend admin/org panels, database layer |

---

## 🏗️ Architecture

```
                         ┌───────────────────────────┐
                         │     SYSTEM ADMIN PANEL     │  (team-c-platform/frontend)
                         │  Orgs · Nodes · FL Rounds  │
                         │  Models · Security · Audit │
                         └─────────────┬───────────────┘
                                       │
                         ┌─────────────▼───────────────┐
                         │        FASTAPI BACKEND       │  (team-c-platform/backend)
                         │  Auth (JWT) · RBAC · Orgs     │
                         │  Nodes · Training Control      │
                         │  Metrics & Reporting APIs      │
                         └───────┬───────────────┬───────┘
                                 │               │
                   ┌─────────────▼───┐   ┌───────▼─────────┐
                   │   PostgreSQL     │   │      Redis       │
                   │ Orgs · Users     │   │ Round State       │
                   │ Nodes · Rounds   │   │ Live Metrics       │
                   │ Model Updates    │   │ Session · Caching  │
                   │ Audit Logs       │   └───────────────────┘
                   └─────────────┬────┘
                                 │
                   ┌─────────────▼──────────────────────┐
                   │   FLOWER FEDERATED LEARNING SERVER   │  (team-a-ai-core/fl)
                   │ Start/Stop Rounds · Distribute Model  │
                   │ Collect Updates · Track Round Status   │
                   └───┬─────────────┬─────────────┬───────┘
                       │             │             │
              ┌────────▼───┐  ┌──────▼─────┐ ┌─────▼──────┐
              │  Org A      │  │  Org B      │ │  Org C      │
              │  Training   │  │  Training   │ │  Training   │  (team-a-ai-core/
              │  Node       │  │  Node       │ │  Node       │   training_node)
              │  ↕ Private  │  │  ↕ Private  │ │  ↕ Private  │
              │    Data     │  │    Data     │ │    Data     │
              └────────┬────┘  └──────┬──────┘ └─────┬───────┘
                       └───────────────┴───────────────┘
                                       │  (model updates only)
                       ┌───────────────▼────────────────┐
                       │      SECURE AGGREGATION          │  (team-b-privacy-security/
                       │ Mask Updates · Aggregate · Dropout│   secure_aggregation)
                       └───────────────┬────────────────┘
                                       │
                       ┌───────────────▼────────────────┐
                       │      DIFFERENTIAL PRIVACY        │  (team-b-privacy-security/
                       │ Clip Updates · Add Noise · ε/δ    │   differential_privacy)
                       └───────────────┬────────────────┘
                                       │
                       ┌───────────────▼────────────────┐
                       │      GLOBAL MODEL STORE          │  (team-a-ai-core/model +
                       │ v1 · v2 · v3 · Versioning/Rollback│   team-c-platform/database)
                       └───────┬───────────────────┬─────┘
                    (next round)                (serve)
                               │                   │
                               │       ┌────────────▼────────────┐
                               │       │    MODEL SERVING API      │  (team-c-platform/backend)
                               │       │ Inference · Auth · Version │
                               │       └────────────┬────────────┘
                               │       ┌────────────▼────────────┐
                               │       │     PREDICTION ENGINE     │  (team-a-ai-core/model)
                               │       │ Load Model · Predict       │
                               │       └───┬────────┬────────┬───┘
                               │           ▼        ▼        ▼
                               │      Users(A)  Users(B)  Users(C)
                               │
                   ┌───────────▼────────────┐
                   │   MONITORING & AUDIT     │  (team-c-platform/backend +
                   │ Logs · Accuracy/Loss     │   team-b-privacy-security)
                   │ Privacy Metrics · Events │
                   └──────────────────────────┘
```

---

## 📁 Repository Structure

```
federix/
│
├── README.md
├── LICENSE
├── .gitignore
├── .env.example
├── docker-compose.yml
├── requirements.txt
│
├── docs/                          # Project-wide documentation
│   ├── architecture/                  # System design docs, diagrams
│   ├── api/                            # API usage guides
│   ├── federated-learning/              # FL theory & round lifecycle docs
│   ├── privacy/                          # Secure Aggregation & DP theory
│   └── development/                       # Dev setup, conventions, workflows
│
├── contracts/                      # Shared schemas/interfaces between teams
│   ├── model/
│   │   ├── model_schema.py             # Model metadata & versioning contract
│   │   └── README.md
│   ├── training/
│   │   ├── training_schema.py          # Round/training request-response contract
│   │   └── README.md
│   ├── privacy/
│   │   ├── aggregation_schema.py       # Aggregation & DP parameter contract
│   │   └── README.md
│   └── api/
│       └── openapi.yaml                # Full REST API contract
│
├── team-a-ai-core/                 # Model + local training + FL orchestration
│   ├── model/
│   │   ├── federix_model.py            # Model architecture definition
│   │   ├── model_config.py             # Hyperparameters & architecture config
│   │   └── serialization.py            # Weight (de)serialization for transport
│   ├── data/
│   │   ├── dataset.py                  # Dataset loading utilities
│   │   ├── partition.py                # Local data partitioning
│   │   └── non_iid.py                  # Non-IID data simulation/handling
│   ├── training/
│   │   ├── train.py                    # Local training loop
│   │   ├── evaluate.py                 # Local/global evaluation
│   │   └── metrics.py                  # Accuracy/loss/metric computation
│   ├── training_node/
│   │   └── node.py                     # Org-side deployable training node entrypoint
│   ├── fl/
│   │   ├── client.py                   # Flower client (per-org)
│   │   ├── server.py                   # Flower server entrypoint
│   │   └── strategy.py                 # Custom FL strategy (aggregation hooks)
│   ├── tests/
│   ├── requirements.txt
│   └── README.md
│
├── team-b-privacy-security/        # Secure Aggregation, DP, and platform security
│   ├── secure_aggregation/
│   │   ├── masking.py                  # Update masking for secure aggregation
│   │   ├── aggregation.py              # Masked aggregation logic
│   │   └── dropout.py                  # Participant dropout handling
│   ├── differential_privacy/
│   │   ├── noise.py                    # Clipping + Gaussian noise mechanisms
│   │   ├── budget.py                   # Privacy budget (ε/δ) management
│   │   └── accountant.py               # Cumulative privacy spend tracking
│   ├── security/
│   │   ├── encryption.py               # Transport/at-rest encryption utilities
│   │   ├── credentials.py              # Credential handling & secrets
│   │   └── validation.py               # Input/update validation & sanitization
│   ├── tests/
│   ├── requirements.txt
│   └── README.md
│
├── team-c-platform/                # Backend API, frontend UI, database
│   ├── backend/
│   │   ├── app/
│   │   │   ├── main.py                 # FastAPI app entrypoint
│   │   │   ├── api/                    # Route definitions
│   │   │   ├── models/                 # ORM/DB models
│   │   │   ├── schemas/                # Pydantic request/response schemas
│   │   │   ├── services/               # Business logic layer
│   │   │   └── auth/                   # JWT auth & RBAC
│   │   └── tests/
│   ├── frontend/
│   │   ├── src/
│   │   │   ├── pages/                  # Admin panel / org panel pages
│   │   │   ├── components/             # Reusable UI components
│   │   │   ├── services/               # API client layer
│   │   │   └── types/                  # Shared TypeScript types
│   │   └── tests/
│   ├── database/
│   │   ├── migrations/                 # Schema migrations
│   │   └── seed/                       # Seed/fixture data
│   └── README.md
│
├── integration/                    # Cross-team integration testing
│   ├── tests/                          # End-to-end FL round tests
│   ├── scripts/                        # Integration test runners/helpers
│   └── docker/                         # Compose files for integration envs
│
└── deployment/                     # Deployment configuration
    ├── docker/                         # Per-service Dockerfiles
    └── kubernetes/                     # K8s manifests/Helm charts
```

---

## ⚙️ Core Components

### 🖥️ System Admin Panel
`team-c-platform/frontend`

| Feature | Description | Status |
|---------|-------------|--------|
| **Organization Management** | Manage organizations and nodes | ✅ Built |
| **FL Round Control** | Start/stop/monitor FL round lifecycle | ✅ Built |
| **Model Management** | Version, promote, rollback models | ✅ Built |
| **Security Config** | Configure privacy/security parameters | ✅ Built |
| **Audit Logs** | View full audit trail | ✅ Built |

---

### 🌐 FastAPI Backend
`team-c-platform/backend`

Central API gateway: JWT authentication, RBAC, organization & node management, training control APIs, and metrics/reporting APIs. Persists to **PostgreSQL** (durable system of record) and **Redis** (live round state, metrics, caching).

---

### 🌸 Flower FL Server & Client
`team-a-ai-core/fl`

Orchestrates the FL lifecycle: starts/stops rounds, distributes the global model, collects local updates, coordinates participants, tracks round status. `strategy.py` is where Secure Aggregation and Differential Privacy hooks plug into the aggregation step.

---

### 🏢 Organization Training Node
`team-a-ai-core/training_node`, `training/`, `data/`

Deployable client run by each organization: loads the org's **Private Data** (never leaves the org), partitions/prepares it (including non-IID handling), trains the received global model locally, evaluates it, and returns only the resulting model update.

---

### 🔒 Secure Aggregation
`team-b-privacy-security/secure_aggregation`

Masks each organization's update, aggregates them so no single contribution is ever visible in isolation, and handles participant dropout gracefully.

---

### 📊 Differential Privacy
`team-b-privacy-security/differential_privacy`

Runs immediately after Secure Aggregation: clips update magnitudes, adds calibrated Gaussian noise, and tracks the cumulative privacy budget (ε/δ) across rounds via the accountant module.

---

### 🔑 Security
`team-b-privacy-security/security`

Encryption for data in transit/at rest, credential management, and input/update validation across the platform.

---

### 💾 Global Model Store
`team-a-ai-core/model` + `team-c-platform/database`

Versioned model storage (v1, v2, v3, …) with rollback support — the source of truth distributed each round and used for serving.

---

### 🚀 Model Serving API & Prediction Engine
`team-c-platform/backend` + `team-a-ai-core/model`

Exposes an authenticated inference endpoint, loads the current global model version, and returns predictions to end users of each organization.

---

### 📈 Monitoring & Audit
`team-c-platform/backend`, cross-cutting

Training logs, round/aggregation status, accuracy/loss, participant activity, privacy metrics (ε/δ spend), and security events — all surfaced through the Metrics & Reporting APIs.

---

## 🔄 Data Flow

1. A **System Admin** starts a federated learning round via the platform.
2. The **Flower server** (`team-a-ai-core/fl/server.py`) pulls the current model from the **Global Model Store** and distributes it to each org's **Flower client**.
3. Each **Training Node** (`team-a-ai-core/training_node`) trains the model locally on **Private Data** — data never leaves the organization.
4. Each org sends back only its **model update** to the Flower server.
5. **Secure Aggregation** (`team-b-privacy-security/secure_aggregation`) combines all updates so no single org's contribution is ever visible in isolation.
6. **Differential Privacy** (`team-b-privacy-security/differential_privacy`) clips and noises the aggregated update, enforcing a formal (ε, δ) guarantee.
7. The resulting model is saved as a new version in the **Global Model Store**.
8. The new version is distributed for the **next FL round**, or promoted to the **Model Serving API** for production inference.
9. **Monitoring & Audit** logs every step throughout.

---

## 🛠️ Tech Stack

| Layer | Technology | Badge |
|-------|-----------|-------|
| Backend API | FastAPI (Python) | ![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=flat-square&logo=fastapi&logoColor=white) |
| FL Orchestration | Flower | ![Flower](https://img.shields.io/badge/Flower-FF6F61?style=flat-square) |
| Local Model Training | PyTorch / TensorFlow | ![PyTorch](https://img.shields.io/badge/PyTorch-EE4C2C?style=flat-square&logo=pytorch&logoColor=white) |
| Relational Storage | PostgreSQL | ![PostgreSQL](https://img.shields.io/badge/PostgreSQL-4169E1?style=flat-square&logo=postgresql&logoColor=white) |
| Cache / Real-time State | Redis | ![Redis](https://img.shields.io/badge/Redis-DC382D?style=flat-square&logo=redis&logoColor=white) |
| Differential Privacy | Opacus (PyTorch) / TensorFlow Privacy | ![Opacus](https://img.shields.io/badge/Opacus-7B1FA2?style=flat-square) |
| Auth | JWT | ![JWT](https://img.shields.io/badge/JWT-000000?style=flat-square&logo=jsonwebtokens&logoColor=white) |
| Frontend | React/TypeScript | ![React](https://img.shields.io/badge/React-61DAFB?style=flat-square&logo=react&logoColor=black) |
| Containerization | Docker, Docker Compose, Kubernetes | ![Docker](https://img.shields.io/badge/Docker-2496ED?style=flat-square&logo=docker&logoColor=white) |

---

## 🚀 Getting Started

### 📋 Prerequisites
- Python 3.10+
- Node.js 18+ (for `team-c-platform/frontend`)
- Docker & Docker Compose
- PostgreSQL 14+
- Redis 6+

### 📥 Clone and Install

```bash
git clone https://github.com/<your-org>/federix.git
cd federix

# Root-level shared dependencies
python -m venv venv
source venv/bin/activate       # Windows: venv\Scripts\activate
pip install -r requirements.txt

# Per-team dependencies (each team can also work independently)
pip install -r team-a-ai-core/requirements.txt
pip install -r team-b-privacy-security/requirements.txt
pip install -r team-c-platform/backend/requirements.txt

# Frontend
cd team-c-platform/frontend
npm install
cd ../../..
```

### 🔧 Environment Setup

```bash
cp .env.example .env
```

```env
# Backend (team-c-platform)
DATABASE_URL=postgresql://user:password@localhost:5432/federix
REDIS_URL=redis://localhost:6379/0
JWT_SECRET=your-secret-key

# FL server (team-a-ai-core)
FLOWER_SERVER_ADDRESS=0.0.0.0:8080
MIN_FIT_CLIENTS=3
NUM_ROUNDS=50

# Differential Privacy (team-b-privacy-security)
DP_CLIP_NORM=1.0
DP_NOISE_MULTIPLIER=1.1
DP_TARGET_EPSILON=3.0
DP_TARGET_DELTA=0.00001
```

### 🐳 Run Everything with Docker Compose

```bash
docker-compose up --build
```

This starts the backend, database, cache, FL server, and serving API as defined in `docker-compose.yml`. For per-service Dockerfiles and Kubernetes manifests, see `deployment/`.

### ▶️ Run Components Individually

```bash
# Backend API
uvicorn team-c-platform.backend.app.main:app --reload --port 8000

# Frontend
cd team-c-platform/frontend && npm run dev

# Flower FL server
python team-a-ai-core/fl/server.py

# An organization's training node
python team-a-ai-core/training_node/node.py --org-id=org_a --server=localhost:8080
```

---

## ⚙️ Configuration

| Parameter | Description | Default |
|-----------|-------------|---------|
| `MIN_FIT_CLIENTS` | Minimum organizations required per round | `3` |
| `NUM_ROUNDS` | Total number of FL rounds to run | `50` |
| `DP_CLIP_NORM` | Max L2 norm per update before noising | `1.0` |
| `DP_NOISE_MULTIPLIER` | Gaussian noise scale (higher = more private) | `1.1` |
| `DP_TARGET_EPSILON` | Total privacy budget for training lifetime | `3.0` |
| `DP_TARGET_DELTA` | Failure probability bound | `1e-5` |
| `JWT_EXPIRY` | Access token lifetime | `1h` |

---

## 🏋️ Running a Federated Training Round

1. **Register organizations and nodes** via the System Admin Panel.
2. **Start each organization's training node** (`team-a-ai-core/training_node/node.py`) so it connects to the Flower server and awaits the next round.
3. **Trigger a training round**:
   ```bash
   curl -X POST http://localhost:8000/api/training/start \
     -H "Authorization: Bearer <token>" \
     -d '{"num_rounds": 10}'
   ```
4. The Flower server distributes the current global model, waits for all orgs to submit updates, runs Secure Aggregation + Differential Privacy (via `team-a-ai-core/fl/strategy.py` calling into `team-b-privacy-security`), and stores the new model version.
5. **Monitor progress** live via the admin dashboard (accuracy, loss, round status, ε/δ spent).
6. Once training completes, promote the latest model version to the **Model Serving API** for production use.

---

## 🔐 Privacy & Security

| Mechanism | Description |
|-----------|-------------|
| **🏠 Data Locality** | Raw data never leaves an organization's infrastructure; only model updates are transmitted |
| **🎭 Secure Aggregation** | The server never observes any single organization's update in isolation, only the masked combined aggregate |
| **📊 Differential Privacy** | Clipping + calibrated Gaussian noise applied to the aggregate, giving a formal (ε, δ) guarantee against membership inference, model inversion, and gradient leakage attacks |
| **📒 Privacy Budget Tracking** | Cumulative ε/δ is tracked every round via `accountant.py` and surfaced in Monitoring & Audit; training halts once the configured budget is exhausted |
| **🔑 Encryption & Credentials** | Encryption utilities and credential/secret handling across the platform |
| **🛂 RBAC & JWT Auth** | All API access is scoped by role (system admin / org admin / org user) |
| **📝 Audit Logging** | Every administrative action, training round, and aggregation event is logged for compliance |

Full theory and implementation notes live in `docs/privacy/`.

---

## 📈 Monitoring & Audit

Tracked per round and system-wide:
- 📋 Training logs and round status
- 🔄 Aggregation status
- 📊 Model accuracy / loss
- 👥 Participant activity
- 🔒 Privacy metrics (ε / δ spent)
- 🚨 Security events

All metrics are queryable via the Metrics & Reporting APIs and viewable in the System Admin Panel.

---

## 🔮 Model Serving / Inference

Once a global model version is finalized, the **Model Serving API** exposes an authenticated inference endpoint and the **Prediction Engine** loads that version's weights to process requests:

```bash
curl -X POST http://localhost:8000/api/predict \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{"input": [...]}'
```

---

## 📜 Contracts (Cross-Team Interfaces)

The `contracts/` directory defines the shared interfaces all three teams build against, so each team can develop independently without breaking integration:

| Contract | Defines |
|----------|---------|
| `contracts/model/model_schema.py` | Model metadata, versioning, and serialization format |
| `contracts/training/training_schema.py` | Training round request/response structure |
| `contracts/privacy/aggregation_schema.py` | Secure aggregation & DP parameter structure |
| `contracts/api/openapi.yaml` | Full REST API contract for the backend |

> ⚠️ Any change to a contract should be reviewed by all three teams before merging, since it's a breaking-change surface across `team-a-ai-core`, `team-b-privacy-security`, and `team-c-platform`.

---

## 👥 Team Ownership

| Directory | Owner | Responsibility |
|-----------|-------|---------------|
| `team-a-ai-core/` | 🤖 AI Core Team | Model architecture, local training, FL client/server |
| `team-b-privacy-security/` | 🔐 Privacy & Security Team | Secure Aggregation, Differential Privacy, platform security |
| `team-c-platform/` | 🖥️ Platform Team | Backend API, frontend, database |
| `contracts/` | 🤝 Shared / Tech Leads | Cross-team interface definitions |
| `integration/` | 🤝 Shared | End-to-end integration testing across all teams |
| `deployment/` | 🖥️ Platform Team | Docker/Kubernetes deployment configuration |

---

## 🧪 Testing

Each team maintains its own unit tests:

```bash
# Team A
pytest team-a-ai-core/tests/

# Team B
pytest team-b-privacy-security/tests/

# Team C (backend)
pytest team-c-platform/backend/tests/

# Team C (frontend)
cd team-c-platform/frontend && npm test
```

Cross-team, end-to-end federated round tests live in `integration/tests/` and are run via:

```bash
bash integration/scripts/run_e2e.sh
```

---

## 🚢 Deployment

- **Docker**: per-service Dockerfiles in `deployment/docker/`, orchestrated locally via the root `docker-compose.yml`.
- **Kubernetes**: manifests/Helm charts in `deployment/kubernetes/` for staging/production clusters.

```bash
kubectl apply -f deployment/kubernetes/
```

---

## 🤝 Contributing

1. Fork the repository and create a feature branch from the relevant team directory.
2. Follow existing code style and add tests under the appropriate `tests/` folder.
3. If your change touches a file under `contracts/`, flag it for review by all three teams before merging.
4. Any change to the privacy pipeline (`team-b-privacy-security/secure_aggregation` or `differential_privacy`) must include updated documentation and must not silently alter the effective privacy guarantee.
5. Open a pull request describing the change, its motivation, and which team(s) it affects.

---

## 📄 License

See [`LICENSE`](./LICENSE).