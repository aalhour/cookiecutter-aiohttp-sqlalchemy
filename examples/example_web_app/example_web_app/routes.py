"""
Routes module.

Responsible for providing the means to register the application routes.
"""
from aiohttp import web

from example_web_app.controllers.example_api import ExampleApiController
from example_web_app.controllers.health_api import HealthApiController


def setup_routes(app: web.Application) -> None:
    """
    Set up all application routes.

    Args:
        app: The aiohttp Application instance
    """
    health_api = HealthApiController()
    example_api = ExampleApiController()

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
    # INTERNAL API ROUTES
    #
    # Add your internal/administrative API routes here
    #
    app.router.add_get('/api/-/health', health_api.get)
