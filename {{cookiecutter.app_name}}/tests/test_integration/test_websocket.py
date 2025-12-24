"""
Integration tests for WebSocket endpoints.

Tests the full WebSocket lifecycle including connection, messaging, and disconnection.
"""
import asyncio
import json

import pytest
from aiohttp import WSMsgType


class TestWebSocketEcho:
    """Integration tests for the echo WebSocket endpoint."""

    async def test_echo_returns_message(self, client):
        """Test that echo endpoint echoes back the message."""
        async with client.ws_connect("/api/v1.0/ws/echo") as ws:
            # Send a message
            await ws.send_json({"message": "Hello, WebSocket!"})

            # Receive the echo
            msg = await ws.receive()
            assert msg.type == WSMsgType.TEXT

            data = json.loads(msg.data)
            assert data["type"] == "echo"
            assert data["data"]["message"] == "Hello, WebSocket!"

    async def test_echo_handles_multiple_messages(self, client):
        """Test that echo handles multiple messages in sequence."""
        async with client.ws_connect("/api/v1.0/ws/echo") as ws:
            for i in range(3):
                await ws.send_json({"count": i})
                msg = await ws.receive()
                data = json.loads(msg.data)
                assert data["data"]["count"] == i

    async def test_echo_returns_error_for_invalid_json(self, client):
        """Test that invalid JSON returns an error."""
        async with client.ws_connect("/api/v1.0/ws/echo") as ws:
            await ws.send_str("not valid json")
            msg = await ws.receive()
            data = json.loads(msg.data)
            assert "error" in data
            assert data["error"] == "Invalid JSON"


class TestWebSocketBroadcast:
    """Integration tests for the broadcast WebSocket endpoint."""

    async def test_broadcast_sends_to_multiple_clients(self, client):
        """Test that broadcast sends messages to all connected clients."""
        # Connect two clients
        async with client.ws_connect("/api/v1.0/ws/broadcast") as ws1:
            async with client.ws_connect("/api/v1.0/ws/broadcast") as ws2:
                # Send a broadcast message from client 1
                await ws1.send_json({"message": "Hello everyone!"})

                # Both clients should receive the message
                msg1 = await asyncio.wait_for(ws1.receive(), timeout=2.0)
                msg2 = await asyncio.wait_for(ws2.receive(), timeout=2.0)

                data1 = json.loads(msg1.data)
                data2 = json.loads(msg2.data)

                assert data1["type"] == "broadcast"
                assert data1["data"]["message"] == "Hello everyone!"
                assert data2["type"] == "broadcast"
                assert data2["data"]["message"] == "Hello everyone!"


class TestWebSocketRoom:
    """Integration tests for the room-based WebSocket endpoint."""

    async def test_room_welcome_message(self, client):
        """Test that joining a room sends a welcome message."""
        async with client.ws_connect("/api/v1.0/ws/room/test-room") as ws:
            msg = await asyncio.wait_for(ws.receive(), timeout=2.0)
            data = json.loads(msg.data)
            assert data["type"] == "welcome"
            assert data["room"] == "test-room"

    async def test_room_message_broadcast(self, client):
        """Test that room messages are broadcast to all room members."""
        async with client.ws_connect("/api/v1.0/ws/room/chat-room") as ws1:
            # Consume welcome message
            await ws1.receive()

            async with client.ws_connect("/api/v1.0/ws/room/chat-room") as ws2:
                # Consume welcome and user_joined messages
                await ws2.receive()
                await ws1.receive()  # ws1 gets user_joined notification

                # Send a message
                await ws1.send_json({"action": "message", "text": "Hello room!"})

                # Both should receive the message
                msg1 = await asyncio.wait_for(ws1.receive(), timeout=2.0)
                msg2 = await asyncio.wait_for(ws2.receive(), timeout=2.0)

                data1 = json.loads(msg1.data)
                data2 = json.loads(msg2.data)

                assert data1["type"] == "room_message"
                assert data1["text"] == "Hello room!"
                assert data2["type"] == "room_message"

    async def test_room_user_count(self, client):
        """Test that list_users action returns correct count."""
        async with client.ws_connect("/api/v1.0/ws/room/count-room") as ws:
            await ws.receive()  # Welcome message

            await ws.send_json({"action": "list_users"})
            msg = await asyncio.wait_for(ws.receive(), timeout=2.0)
            data = json.loads(msg.data)

            assert data["type"] == "user_count"
            assert data["count"] >= 1

    async def test_room_isolation(self, client):
        """Test that messages in one room don't leak to another."""
        async with client.ws_connect("/api/v1.0/ws/room/room-a") as ws_a:
            await ws_a.receive()  # Welcome

            async with client.ws_connect("/api/v1.0/ws/room/room-b") as ws_b:
                await ws_b.receive()  # Welcome

                # Send message to room-a
                await ws_a.send_json({"action": "message", "text": "Room A only"})

                # ws_a should receive it
                msg_a = await asyncio.wait_for(ws_a.receive(), timeout=2.0)
                assert json.loads(msg_a.data)["text"] == "Room A only"

                # ws_b should NOT receive it (timeout expected)
                with pytest.raises(asyncio.TimeoutError):
                    await asyncio.wait_for(ws_b.receive(), timeout=0.5)


class TestWebSocketNotifications:
    """Integration tests for the notifications WebSocket endpoint."""

    async def test_notifications_connect_message(self, client):
        """Test that connecting sends a welcome message."""
        async with client.ws_connect("/api/v1.0/ws/notifications") as ws:
            msg = await asyncio.wait_for(ws.receive(), timeout=2.0)
            data = json.loads(msg.data)
            assert data["type"] == "connected"

    async def test_notifications_subscribe(self, client):
        """Test subscribing to notification topics."""
        async with client.ws_connect("/api/v1.0/ws/notifications") as ws:
            await ws.receive()  # Connected message

            # Subscribe to topics
            await ws.send_json({"action": "subscribe", "topics": ["orders", "alerts"]})
            msg = await asyncio.wait_for(ws.receive(), timeout=2.0)
            data = json.loads(msg.data)

            assert data["type"] == "subscribed"
            assert set(data["topics"]) == {"orders", "alerts"}

    async def test_notifications_unsubscribe(self, client):
        """Test unsubscribing from notification topics."""
        async with client.ws_connect("/api/v1.0/ws/notifications") as ws:
            await ws.receive()  # Connected

            # Subscribe first
            await ws.send_json({"action": "subscribe", "topics": ["orders", "alerts"]})
            await ws.receive()  # Subscribed

            # Unsubscribe from one
            await ws.send_json({"action": "unsubscribe", "topics": ["orders"]})
            msg = await asyncio.wait_for(ws.receive(), timeout=2.0)
            data = json.loads(msg.data)

            assert data["type"] == "unsubscribed"
            assert data["topics"] == ["alerts"]

    async def test_notifications_ping_pong(self, client):
        """Test ping/pong heartbeat."""
        async with client.ws_connect("/api/v1.0/ws/notifications") as ws:
            await ws.receive()  # Connected

            await ws.send_json({"action": "ping"})
            msg = await asyncio.wait_for(ws.receive(), timeout=2.0)
            data = json.loads(msg.data)

            assert data["type"] == "pong"

