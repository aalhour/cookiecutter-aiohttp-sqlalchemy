import asyncio

import uvloop
import pytest
import aiotask_context as context
from aiohttp.test_utils import TestClient, TestServer, unused_port

from example_web_app.app import create_app


asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
TEST_PORT = unused_port()


@pytest.fixture(autouse=True)
def loop_factory():
    # return asyncio.new_event_loop
    return uvloop.EventLoopPolicy


@pytest.fixture(autouse=True)
def set_task_factory(loop):
    loop.set_task_factory(context.task_factory)


@pytest.fixture(autouse=True)
async def server(aiohttp_server) -> TestServer:
    app = create_app()
    server = await aiohttp_server(app, port=TEST_PORT)
    return server


@pytest.fixture()
async def client(aiohttp_client, server) -> TestClient:
    return await aiohttp_client(server)

