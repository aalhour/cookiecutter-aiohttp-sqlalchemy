"""
Unit tests for WebSocket functionality.
"""
from unittest.mock import AsyncMock, MagicMock

import pytest
from aiohttp import web

from {{cookiecutter.app_name}}.core.websocket import WebSocketManager


class TestWebSocketManager:
    """Tests for WebSocketManager class."""

    def test_initial_connection_count_is_zero(self):
        """Test that initial connection count is zero."""
        manager = WebSocketManager()
        assert manager.connection_count == 0

    @pytest.mark.asyncio
    async def test_connect_adds_connection(self):
        """Test that connect adds a connection."""
        manager = WebSocketManager()
        ws = MagicMock(spec=web.WebSocketResponse)

        await manager.connect(ws)

        assert manager.connection_count == 1

    @pytest.mark.asyncio
    async def test_disconnect_removes_connection(self):
        """Test that disconnect removes a connection."""
        manager = WebSocketManager()
        ws = MagicMock(spec=web.WebSocketResponse)

        await manager.connect(ws)
        assert manager.connection_count == 1

        await manager.disconnect(ws)
        assert manager.connection_count == 0

    @pytest.mark.asyncio
    async def test_connect_with_room(self):
        """Test that connections can join rooms."""
        manager = WebSocketManager()
        ws1 = MagicMock(spec=web.WebSocketResponse)
        ws2 = MagicMock(spec=web.WebSocketResponse)

        await manager.connect(ws1, room="room1")
        await manager.connect(ws2, room="room2")

        assert manager.connection_count == 2
        assert "room1" in manager._rooms
        assert "room2" in manager._rooms

    @pytest.mark.asyncio
    async def test_broadcast_sends_to_all_connections(self):
        """Test that broadcast sends to all connections."""
        manager = WebSocketManager()

        ws1 = MagicMock(spec=web.WebSocketResponse)
        ws1.closed = False
        ws1.send_str = AsyncMock()

        ws2 = MagicMock(spec=web.WebSocketResponse)
        ws2.closed = False
        ws2.send_str = AsyncMock()

        await manager.connect(ws1)
        await manager.connect(ws2)

        sent = await manager.broadcast({"type": "test", "data": "hello"})

        assert sent == 2
        ws1.send_str.assert_called_once()
        ws2.send_str.assert_called_once()

    @pytest.mark.asyncio
    async def test_broadcast_to_room_only(self):
        """Test that broadcast to room only sends to room members."""
        manager = WebSocketManager()

        ws1 = MagicMock(spec=web.WebSocketResponse)
        ws1.closed = False
        ws1.send_str = AsyncMock()

        ws2 = MagicMock(spec=web.WebSocketResponse)
        ws2.closed = False
        ws2.send_str = AsyncMock()

        await manager.connect(ws1, room="room1")
        await manager.connect(ws2, room="room2")

        sent = await manager.broadcast({"type": "test"}, room="room1")

        assert sent == 1
        ws1.send_str.assert_called_once()
        ws2.send_str.assert_not_called()

    @pytest.mark.asyncio
    async def test_send_to_specific_connection(self):
        """Test sending to a specific connection."""
        manager = WebSocketManager()

        ws = MagicMock(spec=web.WebSocketResponse)
        ws.closed = False
        ws.send_str = AsyncMock()

        await manager.connect(ws)

        success = await manager.send_to(ws, {"type": "direct", "data": "hello"})

        assert success is True
        ws.send_str.assert_called_once()

    @pytest.mark.asyncio
    async def test_send_to_closed_connection_returns_false(self):
        """Test that sending to closed connection returns False."""
        manager = WebSocketManager()

        ws = MagicMock(spec=web.WebSocketResponse)
        ws.closed = True

        success = await manager.send_to(ws, {"type": "test"})

        assert success is False

    @pytest.mark.asyncio
    async def test_broadcast_skips_closed_connections(self):
        """Test that broadcast skips closed connections."""
        manager = WebSocketManager()

        ws1 = MagicMock(spec=web.WebSocketResponse)
        ws1.closed = False
        ws1.send_str = AsyncMock()

        ws2 = MagicMock(spec=web.WebSocketResponse)
        ws2.closed = True

        await manager.connect(ws1)
        await manager.connect(ws2)

        sent = await manager.broadcast({"type": "test"})

        assert sent == 1
        ws1.send_str.assert_called_once()

    @pytest.mark.asyncio
    async def test_broadcast_with_exclude(self):
        """Test that broadcast can exclude a specific connection."""
        manager = WebSocketManager()

        ws1 = MagicMock(spec=web.WebSocketResponse)
        ws1.closed = False
        ws1.send_str = AsyncMock()

        ws2 = MagicMock(spec=web.WebSocketResponse)
        ws2.closed = False
        ws2.send_str = AsyncMock()

        await manager.connect(ws1)
        await manager.connect(ws2)

        sent = await manager.broadcast({"type": "test"}, exclude=ws1)

        assert sent == 1
        ws1.send_str.assert_not_called()
        ws2.send_str.assert_called_once()

    @pytest.mark.asyncio
    async def test_join_and_leave_room(self):
        """Test joining and leaving rooms."""
        manager = WebSocketManager()
        ws = MagicMock(spec=web.WebSocketResponse)

        await manager.connect(ws)
        await manager.join_room(ws, "new-room")

        assert "new-room" in manager.list_rooms()
        assert manager.get_room_count("new-room") == 1

        await manager.leave_room(ws, "new-room")

        assert "new-room" not in manager.list_rooms()

    def test_list_rooms_returns_active_rooms(self):
        """Test that list_rooms returns all active rooms."""
        manager = WebSocketManager()
        assert manager.list_rooms() == []

    def test_get_room_count_for_empty_room(self):
        """Test that get_room_count returns 0 for non-existent room."""
        manager = WebSocketManager()
        assert manager.get_room_count("nonexistent") == 0

