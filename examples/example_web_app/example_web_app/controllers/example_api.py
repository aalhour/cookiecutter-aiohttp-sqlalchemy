"""
Example API Controller demonstrating full CRUD operations with SQLAlchemy 2.0.
Uses Pydantic schemas for request/response validation.
Includes caching with automatic invalidation on writes.
"""
from aiohttp import web
from pydantic import ValidationError

from example_web_app.controllers.base import BaseJsonApiController
from example_web_app.core.cache import cache, invalidate_cache
from example_web_app.core.database import transactional_session
from example_web_app.core.logger import get_logger
from example_web_app.core.openapi import openapi
from example_web_app.models.example import Example
from example_web_app.schemas.example import ExampleCreate, ExampleResponse, ExampleUpdate

_logger = get_logger()

# Cache key prefixes for easy invalidation
CACHE_PREFIX = "examples"
CACHE_TTL = 300  # 5 minutes


class ExampleApiController(BaseJsonApiController):
    """
    Example API Controller demonstrating SQLAlchemy 2.0 async database access
    with full CRUD operations (Create, Read, Update, Delete).

    Uses:
    - Pydantic schemas for request validation and response serialization
    - Redis caching with automatic invalidation on writes
    """

    # ==================== READ OPERATIONS (with caching) ====================

    @openapi(
        summary="List all examples",
        description="Returns all example items. Supports filtering by active status via query param.",
        tags=["Examples"],
        response_model=ExampleResponse,
        responses={200: "List of examples"},
    )
    async def get(self, request: web.Request) -> web.Response:
        """Return all Examples."""
        active_only = request.query.get('active_only', '').lower() == 'true'

        # Use cached version
        response_data = await self._get_all_cached(active_only)
        return self.json_response(body=response_data)

    @cache(ttl=CACHE_TTL, prefix=CACHE_PREFIX, key_builder=lambda self, active_only: f"list:active={active_only}")
    async def _get_all_cached(self, active_only: bool) -> list[dict]:
        """Cached helper for fetching all examples."""
        async with transactional_session() as session:
            examples = await Example.get_all(session, active_only=active_only)
            return [
                ExampleResponse.from_orm_dict(example.serialized).to_json_dict()
                for example in examples
            ]

    @openapi(
        summary="Get example by ID",
        description="Returns a single example item by its unique identifier.",
        tags=["Examples"],
        response_model=ExampleResponse,
        responses={200: "Example found", 404: "Example not found"},
    )
    async def get_by_id(self, request: web.Request) -> web.Response:
        """Return a single Example given its ID."""
        example_id = request.match_info.get('id')

        result = await self._get_by_id_cached(example_id)
        if result is None:
            return self.write_error(404, "The requested example doesn't exist!")

        return self.json_response(body=result)

    @cache(ttl=CACHE_TTL, prefix=CACHE_PREFIX, key_builder=lambda self, example_id: f"item:{example_id}")
    async def _get_by_id_cached(self, example_id: str) -> dict | None:
        """Cached helper for fetching a single example."""
        async with transactional_session() as session:
            example = await Example.get_by_id(example_id, session)
            if example is None:
                return None
            return ExampleResponse.from_orm_dict(example.serialized).to_json_dict()

    # ==================== CREATE OPERATIONS ====================

    @openapi(
        summary="Create a new example",
        description="Creates a new example item with the provided data.",
        tags=["Examples"],
        request_model=ExampleCreate,
        response_model=ExampleResponse,
        responses={201: "Example created", 400: "Invalid JSON", 422: "Validation error"},
    )
    async def create(self, request: web.Request) -> web.Response:
        """Create a new Example."""
        try:
            data = await request.json()
        except Exception:
            return self.write_error(400, "Invalid JSON body")

        # Validate request with Pydantic
        try:
            create_data = ExampleCreate(**data)
        except ValidationError as e:
            return self.json_response(
                body={
                    "error": "validation_error",
                    "message": "Invalid request data",
                    "details": e.errors(),
                },
                status=422,
            )

        async with transactional_session() as session:
            example = await Example.create(
                session=session,
                name=create_data.name,
                description=create_data.description,
                price=float(create_data.price) if create_data.price else None,
                is_active=create_data.is_active,
            )

            response = ExampleResponse.from_orm_dict(example.serialized)

            # Invalidate list cache (new item added)
            await self._invalidate_list_cache()

            _logger.info("example_created", example_id=example.id, name=example.name)

            return self.json_response(
                body=response.to_json_dict(),
                status=201,
            )

    # ==================== UPDATE OPERATIONS ====================

    @openapi(
        summary="Update an example",
        description="Updates an existing example item with the provided data.",
        tags=["Examples"],
        request_model=ExampleUpdate,
        response_model=ExampleResponse,
        responses={200: "Example updated", 400: "Invalid JSON", 404: "Not found", 422: "Validation error"},
    )
    async def update(self, request: web.Request) -> web.Response:
        """Update an existing Example."""
        example_id = request.match_info.get('id')

        try:
            data = await request.json()
        except Exception:
            return self.write_error(400, "Invalid JSON body")

        # Validate request with Pydantic
        try:
            update_data = ExampleUpdate(**data)
        except ValidationError as e:
            return self.json_response(
                body={
                    "error": "validation_error",
                    "message": "Invalid request data",
                    "details": e.errors(),
                },
                status=422,
            )

        async with transactional_session() as session:
            example = await Example.get_by_id(example_id, session)

            if example is None:
                return self.write_error(404, "The requested example doesn't exist!")

            # Build update kwargs from validated data (only non-None values)
            update_kwargs = {}
            if update_data.name is not None:
                update_kwargs['name'] = update_data.name
            if update_data.description is not None:
                update_kwargs['description'] = update_data.description
            if update_data.price is not None:
                update_kwargs['price'] = float(update_data.price)
            if update_data.is_active is not None:
                update_kwargs['is_active'] = update_data.is_active

            await example.update(session=session, **update_kwargs)

            response = ExampleResponse.from_orm_dict(example.serialized)

            # Invalidate caches (item changed)
            await self._invalidate_item_cache(example_id)
            await self._invalidate_list_cache()

            _logger.info("example_updated", example_id=example.id)

            return self.json_response(body=response.to_json_dict())

    # ==================== DELETE OPERATIONS ====================

    @openapi(
        summary="Delete an example",
        description="Deletes an example item by its unique identifier.",
        tags=["Examples"],
        responses={200: "Example deleted", 404: "Not found"},
    )
    async def delete(self, request: web.Request) -> web.Response:
        """Delete an Example by ID."""
        example_id = request.match_info.get('id')

        async with transactional_session() as session:
            deleted = await Example.delete_by_id(example_id, session)

            if not deleted:
                return self.write_error(404, "The requested example doesn't exist!")

            # Invalidate caches (item removed)
            await self._invalidate_item_cache(example_id)
            await self._invalidate_list_cache()

            _logger.info("example_deleted", example_id=example_id)

            return self.json_response(
                body={"message": f"Example {example_id} deleted successfully"},
                status=200,
            )

    # ==================== CACHE HELPERS ====================

    async def _invalidate_item_cache(self, example_id: str) -> None:
        """Invalidate the cache for a specific item."""
        await invalidate_cache(f"{CACHE_PREFIX}:item:{example_id}*")

    async def _invalidate_list_cache(self) -> None:
        """Invalidate all list caches."""
        await invalidate_cache(f"{CACHE_PREFIX}:list:*")
