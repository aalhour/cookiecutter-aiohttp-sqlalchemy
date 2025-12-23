"""
Example API Controller demonstrating full CRUD operations with SQLAlchemy 2.0.
"""
from aiohttp import web

from {{cookiecutter.app_name}}.controllers.base import BaseJsonApiController
from {{cookiecutter.app_name}}.database import transactional_session
from {{cookiecutter.app_name}}.logger import get_logger
from {{cookiecutter.app_name}}.models.example import Example

_logger = get_logger()


class ExampleApiController(BaseJsonApiController):
    """
    Example API Controller demonstrating SQLAlchemy 2.0 async database access
    with full CRUD operations (Create, Read, Update, Delete).
    """

    # ==================== READ OPERATIONS ====================

    async def get(self, request: web.Request) -> web.Response:
        """
        Return all Examples.

        GET /api/v1.0/examples
        Query params:
            - active_only: If "true", only return active items
        """
        active_only = request.query.get('active_only', '').lower() == 'true'

        async with transactional_session() as session:
            examples = await Example.get_all(session, active_only=active_only)

            return self.json_response(body=[
                example.serialized for example in examples
            ])

    async def get_by_id(self, request: web.Request) -> web.Response:
        """
        Return a single Example given its ID.

        GET /api/v1.0/examples/{id}
        """
        example_id = request.match_info.get('id')

        async with transactional_session() as session:
            example = await Example.get_by_id(example_id, session)

            if example is None:
                return self.write_error(404, "The requested example doesn't exist!")

            return self.json_response(body=example.serialized)

    # ==================== CREATE OPERATIONS ====================

    async def create(self, request: web.Request) -> web.Response:
        """
        Create a new Example.

        POST /api/v1.0/examples
        Body:
            {
                "name": "Example Name",
                "description": "Optional description",
                "price": 19.99,
                "is_active": true
            }
        """
        try:
            data = await request.json()
        except Exception:
            return self.write_error(400, "Invalid JSON body")

        # Validate required fields
        name = data.get('name')
        if not name:
            return self.write_error(400, "Field 'name' is required")

        async with transactional_session() as session:
            example = await Example.create(
                session=session,
                name=name,
                description=data.get('description'),
                price=data.get('price'),
                is_active=data.get('is_active', True)
            )

            return self.json_response(
                body=example.serialized,
                status=201
            )

    # ==================== UPDATE OPERATIONS ====================

    async def update(self, request: web.Request) -> web.Response:
        """
        Update an existing Example.

        PUT /api/v1.0/examples/{id}
        Body:
            {
                "name": "Updated Name",
                "description": "Updated description",
                "price": 29.99,
                "is_active": false
            }
        """
        example_id = request.match_info.get('id')

        try:
            data = await request.json()
        except Exception:
            return self.write_error(400, "Invalid JSON body")

        async with transactional_session() as session:
            example = await Example.get_by_id(example_id, session)

            if example is None:
                return self.write_error(404, "The requested example doesn't exist!")

            # Update with provided fields
            await example.update(
                session=session,
                name=data.get('name'),
                description=data.get('description'),
                price=data.get('price'),
                is_active=data.get('is_active')
            )

            return self.json_response(body=example.serialized)

    # ==================== DELETE OPERATIONS ====================

    async def delete(self, request: web.Request) -> web.Response:
        """
        Delete an Example by ID.

        DELETE /api/v1.0/examples/{id}
        """
        example_id = request.match_info.get('id')

        async with transactional_session() as session:
            deleted = await Example.delete_by_id(example_id, session)

            if not deleted:
                return self.write_error(404, "The requested example doesn't exist!")

            return self.json_response(
                body={"message": f"Example {example_id} deleted successfully"},
                status=200
            )
