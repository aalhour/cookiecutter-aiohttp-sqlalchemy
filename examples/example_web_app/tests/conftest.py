import pytest_asyncio
from aiohttp.test_utils import TestClient, TestServer, unused_port

from example_web_app.app import create_app

TEST_PORT = unused_port()


@pytest_asyncio.fixture
async def server(aiohttp_server) -> TestServer:
    app = create_app()
    server = await aiohttp_server(app, port=TEST_PORT)
    return server


@pytest_asyncio.fixture
async def client(aiohttp_client, server) -> TestClient:
    return await aiohttp_client(server)
