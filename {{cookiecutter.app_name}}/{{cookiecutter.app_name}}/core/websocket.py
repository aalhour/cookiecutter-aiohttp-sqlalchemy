"""
WebSocket utilities for real-time communication.

Provides WebSocket connection management, broadcasting, and room-based messaging.
This module contains the core utilities - API controllers should be in controllers/.
"""
import json
import weakref
from collections.abc import Callable
from datetime import UTC, datetime
from typing import Any

from aiohttp import WSMsgType, web

from {{cookiecutter.app_name}}.core.logger import get_logger

__all__ = [
    "WebSocketManager",
    "ws_manager",
    "websocket_handler",
    "send_notification",
]

_logger = get_logger()


class WebSocketManager:
    """
    Manages WebSocket connections for broadcasting messages.

    Features:
    - Global connection tracking
    - Room-based grouping for targeted broadcasts
    - Automatic cleanup of closed connections
    """

    def __init__(self):
        self._connections: weakref.WeakSet[web.WebSocketResponse] = weakref.WeakSet()
        self._rooms: dict[str, weakref.WeakSet[web.WebSocketResponse]] = {}
        self._connection_metadata: dict[int, dict[str, Any]] = {}

    @property
    def connection_count(self) -> int:
        """Get the number of active connections."""
        return len(self._connections)

    def get_room_count(self, room: str) -> int:
        """Get the number of connections in a specific room."""
        if room not in self._rooms:
            return 0
        return len(self._rooms[room])

    def list_rooms(self) -> list[str]:
        """List all active rooms."""
        return list(self._rooms.keys())

    async def connect(
        self,
        ws: web.WebSocketResponse,
        room: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> None:
        """
        Register a new WebSocket connection.

        Args:
            ws: The WebSocket response object
            room: Optional room name to join
            metadata: Optional metadata to associate with the connection
        """
        self._connections.add(ws)

        if metadata:
            self._connection_metadata[id(ws)] = metadata

        if room:
            if room not in self._rooms:
                self._rooms[room] = weakref.WeakSet()
            self._rooms[room].add(ws)

        _logger.info("websocket_connected", total=self.connection_count, room=room)

    async def disconnect(
        self,
        ws: web.WebSocketResponse,
        room: str | None = None,
    ) -> None:
        """
        Unregister a WebSocket connection.

        Args:
            ws: The WebSocket response object
            room: Optional room name to leave
        """
        self._connections.discard(ws)
        self._connection_metadata.pop(id(ws), None)

        if room and room in self._rooms:
            self._rooms[room].discard(ws)
            if not self._rooms[room]:
                del self._rooms[room]

        _logger.info("websocket_disconnected", total=self.connection_count, room=room)

    async def join_room(self, ws: web.WebSocketResponse, room: str) -> None:
        """Add a connection to a room."""
        if room not in self._rooms:
            self._rooms[room] = weakref.WeakSet()
        self._rooms[room].add(ws)
        _logger.debug("websocket_joined_room", room=room)

    async def leave_room(self, ws: web.WebSocketResponse, room: str) -> None:
        """Remove a connection from a room."""
        if room in self._rooms:
            self._rooms[room].discard(ws)
            if not self._rooms[room]:
                del self._rooms[room]
        _logger.debug("websocket_left_room", room=room)

    async def broadcast(
        self,
        message: dict[str, Any],
        room: str | None = None,
        exclude: web.WebSocketResponse | None = None,
    ) -> int:
        """
        Broadcast a message to all connections or a specific room.

        Args:
            message: The message to send (will be JSON serialized)
            room: Optional room to broadcast to
            exclude: Optional connection to exclude from broadcast

        Returns:
            Number of connections the message was sent to
        """
        connections = self._rooms.get(room, set()) if room else self._connections
        sent = 0

        message_json = json.dumps(message)

        for ws in list(connections):
            if ws.closed or ws is exclude:
                continue
            try:
                await ws.send_str(message_json)
                sent += 1
            except Exception as e:
                _logger.warning("websocket_send_error", error=str(e))

        _logger.debug("websocket_broadcast", room=room, sent=sent)
        return sent

    async def send_to(
        self,
        ws: web.WebSocketResponse,
        message: dict[str, Any],
    ) -> bool:
        """
        Send a message to a specific connection.

        Args:
            ws: The WebSocket connection
            message: The message to send

        Returns:
            True if sent successfully
        """
        if ws.closed:
            return False

        try:
            await ws.send_str(json.dumps(message))
            return True
        except Exception as e:
            _logger.warning("websocket_send_error", error=str(e))
            return False


# Global WebSocket manager
ws_manager = WebSocketManager()


async def websocket_handler(
    request: web.Request,
    on_message: Callable[[web.WebSocketResponse, dict], Any] | None = None,
    on_connect: Callable[[web.WebSocketResponse], Any] | None = None,
    on_disconnect: Callable[[web.WebSocketResponse], Any] | None = None,
    room: str | None = None,
) -> web.WebSocketResponse:
    """
    Generic WebSocket handler with message processing.

    Args:
        request: The aiohttp request
        on_message: Optional callback for incoming messages
        on_connect: Optional callback when connection is established
        on_disconnect: Optional callback when connection is closed
        room: Optional room to join

    Usage in controllers:
        async def my_ws_handler(request):
            async def handle_message(ws, data):
                await ws_manager.send_to(ws, {"echo": data})
            return await websocket_handler(request, on_message=handle_message)
    """
    ws = web.WebSocketResponse(heartbeat=30.0)
    await ws.prepare(request)

    await ws_manager.connect(ws, room)

    if on_connect:
        await on_connect(ws)

    try:
        async for msg in ws:
            if msg.type == WSMsgType.TEXT:
                try:
                    data = json.loads(msg.data)

                    if on_message:
                        await on_message(ws, data)
                    else:
                        # Echo by default
                        await ws_manager.send_to(ws, {"type": "echo", "data": data})

                except json.JSONDecodeError:
                    await ws_manager.send_to(ws, {"error": "Invalid JSON"})

            elif msg.type == WSMsgType.ERROR:
                _logger.error("websocket_error", error=ws.exception())

    finally:
        if on_disconnect:
            await on_disconnect(ws)
        await ws_manager.disconnect(ws, room)

    return ws


async def send_notification(topic: str, message: dict[str, Any]) -> int:
    """
    Send a notification to all subscribers of a topic.

    Args:
        topic: The notification topic
        message: The notification payload

    Returns:
        Number of clients notified
    """
    return await ws_manager.broadcast(
        {
            "type": "notification",
            "topic": topic,
            "data": message,
            "timestamp": datetime.now(UTC).isoformat(),
        },
        room=f"notifications:{topic}",
    )

