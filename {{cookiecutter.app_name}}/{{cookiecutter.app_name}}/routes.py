"""
Routes module.

Responsible for providing the means to register the application routes.
"""

from {{cookiecutter.app_name}}.controllers.health_api import HealthApiController
from {{cookiecutter.app_name}}.controllers.example_api import ExampleApiController


def setup_routes(app):
    ###
    # Register the HelloWorld API handlers
    #

    health_api = HealthApiController()
    example_api = ExampleApiController()

    ###
    # API v1.0 ROUTES
    #
    # Add your public v1.0 API routes here
    #
    app.router.add_get('/api/v1.0/examples', example_api.get)
    app.router.add_get('/api/v1.0/examples/{id}', example_api.get_by_id)

    ###
    # INTERNAL API ROUTES
    #
    # Add your internal/administrative API routes here
    #
    app.router.add_get('/api/-/health', health_api.get)

