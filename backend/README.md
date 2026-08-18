# 🛡️ Privacy-Preserving Federated Learning Platform — Backend (SIH)

This is the orchestration and integration backend layer for the **Privacy-Preserving Federated Learning (PPFL)** platform. It bridges the **React Dashboard frontend**, the **Flower FL Server**, and the **Privacy/Security Module** (Differential Privacy + Secure Aggregation).

---

## 🚀 Key Features

- **Organization Registry**: Register and manage simulated client nodes (e.g., Hospital Alpha, Clinic Beta) and their live status (`idle`, `training`, `done`, `offline`).
- **Federated Training Lifecycle**: Trigger multi-round training runs with customizable rounds, target accuracy, and privacy budget constraints. Gracefully stop active runs at any round.
- **Privacy Budget Tracking**: Tracks round-by-round Differential Privacy expenditure ($\epsilon$-spent) and cumulative privacy budget.
- **Native WebSocket Streaming (`/ws/metrics`)**: Pushes real-time JSON metrics (loss, accuracy, epsilon spent, client node states) directly to the React dashboard.
- **SQLite History Storage**: Automatically stores all past rounds, metrics, run IDs, and duration in SQLite via SQLAlchemy for auditability and dashboard analytics.
- **Decoupled Architecture**: Simulated mode works immediately out-of-the-box. Swapping in real Flower training only requires modifying a single function in `app/services/training_engine.py`.

---

## 📂 Project Structure

```
backend/
├── app/
│   ├── main.py                 # FastAPI application instance, CORS, lifespan & router mounting
│   ├── config.py               # Pydantic Settings (DB URL, CORS origins, default round parameters)
│   ├── database.py             # SQLAlchemy engine, session generator & SQLite table initialization
│   ├── models/                 # SQLAlchemy ORM database models
│   │   ├── __init__.py
│   │   ├── org.py              # Organization model (id, name, status, description, timestamps)
│   │   └── round.py            # RoundHistory model (run_id, accuracy, loss, epsilon, org statuses)
│   ├── schemas/                # Pydantic request/response schemas
│   │   ├── __init__.py
│   │   ├── org.py              # OrgRegister, OrgResponse schemas
│   │   └── round.py            # TrainingStart, TrainingStatus, RoundMetrics & WS schemas
│   ├── routers/                # API route handlers
│   │   ├── __init__.py
│   │   ├── orgs.py             # /orgs/register, /orgs, /orgs/{id}
│   │   ├── training.py         # /training/start, /training/stop, /training/status, /training/history
│   │   └── metrics_ws.py       # /ws/metrics native WebSocket endpoint
│   ├── services/               # Business logic & hardware/FL abstraction
│   │   ├── __init__.py
│   │   ├── ws_manager.py       # Thread-safe WebSocket connection manager (auto-cleanup & broadcast)
│   │   └── training_engine.py  # 🔌 Single file to swap in real Flower / PyTorch / Privacy code
│   └── __init__.py
├── requirements.txt            # Python dependencies
├── run.py                      # CLI entrypoint for running Uvicorn server
└── README.md                   # Complete documentation and Flower integration guide
```

---

## 📦 Installation & Setup

### 1. Create a Virtual Environment

```bash
cd backend
python -m venv venv

# On Windows:
.\venv\Scripts\activate

# On Linux/macOS:
source venv/bin/activate
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Run the Backend Server

```bash
python run.py
```

Or run directly with Uvicorn:

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

- **Interactive Swagger API Docs**: [http://localhost:8000/docs](http://localhost:8000/docs)
- **ReDoc Documentation**: [http://localhost:8000/redoc](http://localhost:8000/redoc)
- **WebSocket Endpoint**: `ws://localhost:8000/ws/metrics`

---

## 📡 REST API Reference

### 1. Organizations

#### Register Organization
```bash
curl -X POST "http://localhost:8000/orgs/register" \
     -H "Content-Type: application/json" \
     -d '{"name": "Hospital Alpha", "description": "Regional cardiology center"}'
```

#### List All Organizations
```bash
curl -X GET "http://localhost:8000/orgs"
```

---

### 2. Training Lifecycle & Status

#### Start Training Run
```bash
curl -X POST "http://localhost:8000/training/start" \
     -H "Content-Type: application/json" \
     -d '{
       "rounds": 5,
       "org_names": ["Hospital Alpha", "Medical Center Beta"],
       "target_accuracy": 0.95,
       "max_epsilon": 5.0
     }'
```

#### Stop Current Training Run
```bash
curl -X POST "http://localhost:8000/training/stop"
```

#### Get Current Training Status
```bash
curl -X GET "http://localhost:8000/training/status"
```

#### Get Training History
```bash
curl -X GET "http://localhost:8000/training/history?limit=20"
```

---

## ⚡ WebSocket Live Metric Streaming (`/ws/metrics`)

Clients (such as your React frontend) connect to `ws://localhost:8000/ws/metrics` to receive real-time JSON events.

### Example JavaScript / React Client:

```javascript
const ws = new WebSocket("ws://localhost:8000/ws/metrics");

ws.onopen = () => {
  console.log("Connected to Federated Shield WebSocket");
};

ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  console.log("Live Event Received:", data);

  switch (data.event) {
    case "status_update":
      console.log("Current state:", data.status);
      break;
    case "training_started":
      console.log(`Training started for run ${data.run_id}`);
      break;
    case "round_complete":
      console.log(`Round ${data.round}/${data.total_rounds}: Accuracy: ${data.accuracy}, Loss: ${data.loss}, Epsilon Spent: ${data.epsilon_spent}`);
      // Update charts & client node statuses here
      break;
    case "training_completed":
      console.log("Training finished successfully!");
      break;
    case "training_stopped":
      console.log("Training halted by user.");
      break;
  }
};

ws.onclose = () => console.log("WebSocket disconnected");
```

### JSON Message Schema Emitted per Round:
```json
{
  "event": "round_complete",
  "run_id": "run_a8f3b92c",
  "round": 3,
  "total_rounds": 5,
  "accuracy": 0.8425,
  "loss": 0.6120,
  "epsilon_spent": 0.4482,
  "cumulative_epsilon": 1.3521,
  "org_statuses": {
    "Hospital Alpha": "training",
    "Medical Center Beta": "training"
  },
  "duration_seconds": 2.51,
  "timestamp": "2026-08-18T19:30:00.000000"
}
```

---

## 🔌 How to Plug in Real Flower & Privacy Code

The training architecture is decoupled. To replace the simulated engine with the real Flower server and Differential Privacy pipeline in `Federated_Shield`:

1. Open [`app/services/training_engine.py`](app/services/training_engine.py).
2. Locate the **`run_round()`** function:

```python
async def run_round(
    self,
    round_num: int,
    total_rounds: int,
    participating_orgs: List[str],
    current_cumulative_epsilon: float,
    previous_accuracy: float,
    previous_loss: float,
    stop_event: asyncio.Event,
) -> Dict[str, Any]:
    # ---------------------------------------------------------
    # 1. Import your Flower FL server & Privacy pipeline:
    #    from fl.server import execute_fl_round
    #    from privacy_security.pipeline import run_privacy_pipeline
    #
    # 2. Trigger Flower federated round:
    #    fl_result = await execute_fl_round(round_num, participating_orgs)
    #
    # 3. Apply Secure Aggregation & Differential Privacy:
    #    dp_result = run_privacy_pipeline(fl_result.weights)
    #
    # 4. Return the resulting dictionary:
    #    return {
    #        "accuracy": fl_result.accuracy,
    #        "loss": fl_result.loss,
    #        "epsilon_spent": dp_result.epsilon,
    #        "cumulative_epsilon": current_cumulative_epsilon + dp_result.epsilon,
    #        "org_statuses": {org: "done" for org in participating_orgs},
    #    }
    # ---------------------------------------------------------
```

All SQLite database saving, WebSocket broadcasting, REST responses, error isolation, and organization status updates will continue working automatically!
