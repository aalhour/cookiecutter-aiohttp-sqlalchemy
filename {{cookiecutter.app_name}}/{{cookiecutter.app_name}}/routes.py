"""
Routes module.

Responsible for providing the means to register the application routes.
"""
from aiohttp import web

from {{cookiecutter.app_name}}.controllers.example_api import ExampleApiController
from {{cookiecutter.app_name}}.controllers.health_api import (
    HealthApiController,
    LivenessApiController,
    ReadinessApiController,
)
from {{cookiecutter.app_name}}.controllers.websocket_api import WebSocketApiController
from {{cookiecutter.app_name}}.middleware import MetricsController


def setup_routes(app: web.Application) -> None:
    """
    Set up all application routes.

    Args:
        app: The aiohttp Application instance
    """
    # Controllers
    health_api = HealthApiController()
    readiness_api = ReadinessApiController()
    liveness_api = LivenessApiController()
    example_api = ExampleApiController()
    metrics_api = MetricsController()
    websocket_api = WebSocketApiController()

    ###
    # INTERNAL / INFRASTRUCTURE ROUTES
    #
    # Health checks, metrics, and monitoring endpoints
    #
    app.router.add_get('/api/-/health', health_api.get)
    app.router.add_get('/api/-/ready', readiness_api.get)
    app.router.add_get('/api/-/live', liveness_api.get)
    app.router.add_get('/metrics', metrics_api.get)

    ###
    # API v1.0 ROUTES - Example CRUD API
    #
    # Full CRUD operations for the Example resource:
    # - GET    /api/v1.0/examples      - List all examples
    # - POST   /api/v1.0/examples      - Create a new example
    # - GET    /api/v1.0/examples/{id} - Get a single example by ID
    # - PUT    /api/v1.0/examples/{id} - Update an example by ID
    # - DELETE /api/v1.0/examples/{id} - Delete an example by ID
    #
    app.router.add_get('/api/v1.0/examples', example_api.get)
    app.router.add_post('/api/v1.0/examples', example_api.create)
    app.router.add_get('/api/v1.0/examples/{id}', example_api.get_by_id)
    app.router.add_put('/api/v1.0/examples/{id}', example_api.update)
    app.router.add_delete('/api/v1.0/examples/{id}', example_api.delete)

    ###
    # WEBSOCKET ROUTES
    #
    # Real-time communication endpoints:
    # - WS /api/v1.0/ws/echo               - Echo messages back to sender
    # - WS /api/v1.0/ws/broadcast          - Broadcast messages to all clients
    # - WS /api/v1.0/ws/room/{room_name}   - Room-based chat
    # - WS /api/v1.0/ws/notifications      - Server-sent notifications
    #
    app.router.add_get('/api/v1.0/ws/echo', websocket_api.echo_handler)
    app.router.add_get('/api/v1.0/ws/broadcast', websocket_api.broadcast_handler)
    app.router.add_get('/api/v1.0/ws/room/{room_name}', websocket_api.room_handler)
    app.router.add_get('/api/v1.0/ws/notifications', websocket_api.notifications_handler)
