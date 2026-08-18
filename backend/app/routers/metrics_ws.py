"""WebSocket router for live federated learning metrics streaming."""

import json
import logging
from datetime import datetime
from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from app.services.ws_manager import ws_manager
from app.services.training_engine import training_engine

logger = logging.getLogger(__name__)

router = APIRouter(tags=["WebSocket Stream"])


@router.websocket("/ws/metrics")
async def websocket_metrics_endpoint(websocket: WebSocket) -> None:
    """Live WebSocket stream endpoint for round metrics, training events, and client node statuses.

    Connect via: `ws://localhost:8000/ws/metrics`
    Pushes events:
      - `status_update` (sent on initial connection)
      - `training_started`
      - `round_complete` {round, accuracy, loss, epsilon_spent, cumulative_epsilon, org_statuses}
      - `training_completed`
      - `training_stopped`
      - `pong`
    """
    await ws_manager.connect(websocket)

    try:
        # Send initial status snapshot to the newly connected client
        initial_status = training_engine.get_status()
        await ws_manager.send_personal_message(
            {
                "event": "status_update",
                "message": "Connected to Federated Shield live metrics stream.",
                **initial_status,
                "timestamp": datetime.utcnow().isoformat(),
            },
            websocket,
        )

        # Keep connection open and handle client-sent messages (like pings or queries)
        while True:
            data = await websocket.receive_text()
            try:
                msg_data = json.loads(data) if data.startswith("{") else {"raw": data}
            except Exception:
                msg_data = {"raw": data}

            # Respond to ping or status inquiry
            if msg_data.get("type") == "ping" or msg_data.get("event") == "ping" or data == "ping":
                await ws_manager.send_personal_message(
                    {"event": "pong", "timestamp": datetime.utcnow().isoformat()},
                    websocket,
                )
            elif msg_data.get("type") == "get_status":
                status_data = training_engine.get_status()
                await ws_manager.send_personal_message(
                    {
                        "event": "status_update",
                        **status_data,
                        "timestamp": datetime.utcnow().isoformat(),
                    },
                    websocket,
                )

    except WebSocketDisconnect:
        logger.info("WebSocket client disconnected normally.")
    except Exception as e:
        logger.warning(f"Unexpected WebSocket disconnection / error: {e}")
    finally:
        await ws_manager.disconnect(websocket)
