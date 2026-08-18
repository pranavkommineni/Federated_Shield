"""WebSocket Connection Manager for live metric streaming."""

import asyncio
import json
import logging
from typing import List, Union, Dict, Any
from fastapi import WebSocket, WebSocketDisconnect
from pydantic import BaseModel

logger = logging.getLogger(__name__)


class WebSocketManager:
    """Manages active WebSocket connections, client lifecycle, and safe broadcast streaming."""

    def __init__(self) -> None:
        self.active_connections: List[WebSocket] = []
        self._lock = asyncio.Lock()

    async def connect(self, websocket: WebSocket) -> None:
        """Accept a new incoming WebSocket connection and register it."""
        await websocket.accept()
        async with self._lock:
            self.active_connections.append(websocket)
        logger.info(f"WebSocket client connected. Active clients: {len(self.active_connections)}")

    async def disconnect(self, websocket: WebSocket) -> None:
        """Safely remove a disconnected client from the active registry."""
        async with self._lock:
            if websocket in self.active_connections:
                self.active_connections.remove(websocket)
        logger.info(f"WebSocket client disconnected. Remaining clients: {len(self.active_connections)}")

    async def send_personal_message(self, message: Union[Dict[str, Any], BaseModel, str], websocket: WebSocket) -> None:
        """Send a JSON payload directly to a specific connected client."""
        try:
            payload = self._serialize_message(message)
            await websocket.send_text(payload)
        except Exception as e:
            logger.warning(f"Failed to send personal message to client: {e}")
            await self.disconnect(websocket)

    async def broadcast(self, message: Union[Dict[str, Any], BaseModel, str]) -> None:
        """Broadcast a message to all active clients.

        Gracefully handles dead or stalled sockets by catching errors and cleaning
        up disconnected clients so one faulty client never crashes or halts the server.
        """
        payload = self._serialize_message(message)

        async with self._lock:
            connections_snapshot = list(self.active_connections)

        if not connections_snapshot:
            return

        dead_connections: List[WebSocket] = []

        for connection in connections_snapshot:
            try:
                await connection.send_text(payload)
            except (WebSocketDisconnect, ConnectionResetError, RuntimeError, Exception) as e:
                logger.warning(f"Error broadcasting to client, marking for removal: {e}")
                dead_connections.append(connection)

        if dead_connections:
            async with self._lock:
                for dead_conn in dead_connections:
                    if dead_conn in self.active_connections:
                        self.active_connections.remove(dead_conn)
            logger.info(f"Cleaned up {len(dead_connections)} dead WebSocket connections.")

    @staticmethod
    def _serialize_message(message: Union[Dict[str, Any], BaseModel, str]) -> str:
        """Helper to serialize dicts, Pydantic models, or strings into JSON."""
        if isinstance(message, BaseModel):
            return message.model_dump_json()
        elif isinstance(message, dict):
            return json.dumps(message, default=str)
        elif isinstance(message, str):
            return message
        else:
            return json.dumps(message, default=str)


# Global singleton manager instance
ws_manager = WebSocketManager()
