"""Routers Package."""

from app.routers.orgs import router as orgs_router
from app.routers.training import router as training_router
from app.routers.metrics_ws import router as metrics_ws_router
from app.routers.users import router as users_router
from app.routers.inference import router as inference_router
from app.routers.node_telemetry import router as node_telemetry_router
from app.routers.chat import router as chat_router

__all__ = [
    "orgs_router",
    "training_router",
    "metrics_ws_router",
    "users_router",
    "inference_router",
    "node_telemetry_router",
    "chat_router",
]
