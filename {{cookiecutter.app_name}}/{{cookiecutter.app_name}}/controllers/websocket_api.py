"""
WebSocket API Controller for real-time communication endpoints.

Provides endpoints for:
- Echo messaging
- Broadcast messaging
- Room-based chat
- Notification subscriptions
"""
from datetime import UTC, datetime

from aiohttp import web

from {{cookiecutter.app_name}}.core.websocket import websocket_handler, ws_manager


class WebSocketApiController:
    """
    WebSocket controller with multiple endpoints for real-time features.

    Endpoints:
    - /api/v1.0/ws/echo - Echo messages back to sender
    - /api/v1.0/ws/broadcast - Broadcast messages to all clients
    - /api/v1.0/ws/room/{room_name} - Room-based chat
    - /api/v1.0/ws/notifications - Server-sent notifications
    """

    async def echo_handler(self, request: web.Request) -> web.WebSocketResponse:
        """
        Echo WebSocket endpoint - echoes back any message received.

        WS /api/v1.0/ws/echo

        Send: {"message": "Hello"}
        Receive: {"type": "echo", "data": {"message": "Hello"}}
        """
        async def handle_message(ws: web.WebSocketResponse, data: dict):
            await ws_manager.send_to(ws, {"type": "echo", "data": data})

        return await websocket_handler(request, on_message=handle_message)

    async def broadcast_handler(self, request: web.Request) -> web.WebSocketResponse:
        """
        Broadcast WebSocket endpoint - messages are broadcast to all connected clients.

        WS /api/v1.0/ws/broadcast

        Send: {"message": "Hello everyone"}
        All clients receive: {"type": "broadcast", "data": {"message": "Hello everyone"}}
        """
        async def handle_message(ws: web.WebSocketResponse, data: dict):
            await ws_manager.broadcast(
                {"type": "broadcast", "data": data, "timestamp": datetime.now(UTC).isoformat()},
                room="broadcast",
            )

        return await websocket_handler(request, on_message=handle_message, room="broadcast")

    async def room_handler(self, request: web.Request) -> web.WebSocketResponse:
        """
        Room-based chat WebSocket endpoint.

        WS /api/v1.0/ws/room/{room_name}

        Messages are broadcast only to users in the same room.
        Supports commands:
        - {"action": "message", "text": "Hello room"} - Send message to room
        - {"action": "list_users"} - Get count of users in room
        """
        room_name = request.match_info.get("room_name", "default")

        async def on_connect(ws: web.WebSocketResponse):
            # Notify room that a new user joined
            await ws_manager.broadcast(
                {
                    "type": "user_joined",
                    "room": room_name,
                    "users": ws_manager.get_room_count(room_name),
                    "timestamp": datetime.now(UTC).isoformat(),
                },
                room=room_name,
                exclude=ws,
            )
            # Send welcome message to the new user
            await ws_manager.send_to(ws, {
                "type": "welcome",
                "room": room_name,
                "users": ws_manager.get_room_count(room_name),
            })

        async def on_disconnect(ws: web.WebSocketResponse):
            # Notify room that a user left
            await ws_manager.broadcast(
                {
                    "type": "user_left",
                    "room": room_name,
                    "users": ws_manager.get_room_count(room_name) - 1,
                    "timestamp": datetime.now(UTC).isoformat(),
                },
                room=room_name,
                exclude=ws,
            )

        async def handle_message(ws: web.WebSocketResponse, data: dict):
            action = data.get("action", "message")

            if action == "message":
                # Broadcast message to room
                text = data.get("text", "")
                await ws_manager.broadcast(
                    {
                        "type": "room_message",
                        "room": room_name,
                        "text": text,
                        "timestamp": datetime.now(UTC).isoformat(),
                    },
                    room=room_name,
                )
            elif action == "list_users":
                await ws_manager.send_to(ws, {
                    "type": "user_count",
                    "room": room_name,
                    "count": ws_manager.get_room_count(room_name),
                })
            else:
                await ws_manager.send_to(ws, {"error": f"Unknown action: {action}"})

        return await websocket_handler(
            request,
            on_message=handle_message,
            on_connect=on_connect,
            on_disconnect=on_disconnect,
            room=room_name,
        )

    async def notifications_handler(self, request: web.Request) -> web.WebSocketResponse:
        """
        Notifications WebSocket endpoint - receive server-sent notifications.

        WS /api/v1.0/ws/notifications

        This endpoint is primarily for receiving server-sent events.
        Clients can subscribe to different notification types:
        - {"action": "subscribe", "topics": ["orders", "alerts"]}
        - {"action": "unsubscribe", "topics": ["orders"]}
        """
        subscribed_topics: set[str] = set()

        async def on_connect(ws: web.WebSocketResponse):
            await ws_manager.send_to(ws, {
                "type": "connected",
                "message": "Connected to notifications. Subscribe to topics using {action: 'subscribe', topics: [...]}",
            })

        async def handle_message(ws: web.WebSocketResponse, data: dict):
            nonlocal subscribed_topics
            action = data.get("action")

            if action == "subscribe":
                topics = data.get("topics", [])
                for topic in topics:
                    subscribed_topics.add(topic)
                    await ws_manager.join_room(ws, f"notifications:{topic}")
                await ws_manager.send_to(ws, {
                    "type": "subscribed",
                    "topics": list(subscribed_topics),
                })

            elif action == "unsubscribe":
                topics = data.get("topics", [])
                for topic in topics:
                    subscribed_topics.discard(topic)
                    await ws_manager.leave_room(ws, f"notifications:{topic}")
                await ws_manager.send_to(ws, {
                    "type": "unsubscribed",
                    "topics": list(subscribed_topics),
                })

            elif action == "ping":
                await ws_manager.send_to(ws, {"type": "pong"})

            else:
                await ws_manager.send_to(ws, {"error": f"Unknown action: {action}"})

        async def on_disconnect(ws: web.WebSocketResponse):
            # Clean up subscriptions
            for topic in subscribed_topics:
                await ws_manager.leave_room(ws, f"notifications:{topic}")

        return await websocket_handler(
            request,
            on_message=handle_message,
            on_connect=on_connect,
            on_disconnect=on_disconnect,
        )

