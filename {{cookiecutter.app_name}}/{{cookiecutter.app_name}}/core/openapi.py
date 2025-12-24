"""
OpenAPI documentation generator for class-based controllers.

Uses decorators to annotate controller methods with OpenAPI metadata,
then generates the full OpenAPI spec from Pydantic schemas.

Usage:
    from {{cookiecutter.app_name}}.core.openapi import openapi

    class MyController(BaseJsonApiController):
        @openapi(
            summary="Get all items",
            tags=["Items"],
            response_model=ItemResponse,
        )
        async def get(self, request: web.Request) -> web.Response:
            ...
"""
from functools import wraps
from typing import Any

from aiohttp import web
from pydantic import BaseModel


# Store for OpenAPI metadata attached to handler functions
_openapi_registry: dict[str, dict[str, Any]] = {}


def openapi(
    *,
    summary: str = "",
    description: str = "",
    tags: list[str] | None = None,
    request_model: type[BaseModel] | None = None,
    response_model: type[BaseModel] | None = None,
    responses: dict[int, str] | None = None,
    deprecated: bool = False,
):
    """
    Decorator to add OpenAPI metadata to a controller method.

    Args:
        summary: Short summary of the endpoint
        description: Detailed description (supports markdown)
        tags: List of tags for grouping in docs
        request_model: Pydantic model for request body validation
        response_model: Pydantic model for response serialization
        responses: Additional response codes and descriptions
        deprecated: Mark endpoint as deprecated
    """
    def decorator(func):
        # Store metadata on the function
        func._openapi_meta = {
            "summary": summary or func.__doc__,
            "description": description,
            "tags": tags or [],
            "request_model": request_model,
            "response_model": response_model,
            "responses": responses or {},
            "deprecated": deprecated,
        }

        @wraps(func)
        async def wrapper(*args, **kwargs):
            return await func(*args, **kwargs)

        wrapper._openapi_meta = func._openapi_meta
        return wrapper

    return decorator


def generate_openapi_spec(
    app: web.Application,
    title: str = "API",
    version: str = "1.0.0",
    description: str = "",
) -> dict[str, Any]:
    """
    Generate OpenAPI 3.0 specification from registered routes.

    Inspects all routes, finds methods with @openapi decorator,
    and builds the spec using Pydantic model schemas.
    """
    paths: dict[str, dict[str, Any]] = {}
    schemas: dict[str, dict[str, Any]] = {}
    tags_set: set[str] = set()

    # Iterate through all routes
    for resource in app.router.resources():
        path = resource.canonical
        if not path:
            continue

        # Convert aiohttp path params to OpenAPI format
        openapi_path = path
        path_params = []
        for part in path.split("/"):
            if part.startswith("{") and part.endswith("}"):
                param_name = part[1:-1]
                path_params.append({
                    "name": param_name,
                    "in": "path",
                    "required": True,
                    "schema": {"type": "string"},
                })

        for route in resource:
            method = route.method.lower()
            if method == "*":
                continue

            handler = route.handler

            # Check if handler has OpenAPI metadata
            meta = getattr(handler, "_openapi_meta", None)
            if meta is None:
                # Try to get from class method if it's a bound method
                if hasattr(handler, "__self__"):
                    meta = getattr(handler.__func__, "_openapi_meta", None)

            if meta is None:
                # Generate basic metadata from docstring
                meta = {
                    "summary": (handler.__doc__ or "").split("\n")[0].strip(),
                    "description": "",
                    "tags": [],
                    "request_model": None,
                    "response_model": None,
                    "responses": {},
                    "deprecated": False,
                }

            # Build operation object
            operation: dict[str, Any] = {
                "summary": meta["summary"],
                "responses": {"200": {"description": "Success"}},
            }

            if meta["description"]:
                operation["description"] = meta["description"]

            if meta["tags"]:
                operation["tags"] = meta["tags"]
                tags_set.update(meta["tags"])

            if meta["deprecated"]:
                operation["deprecated"] = True

            # Add path parameters
            if path_params:
                operation["parameters"] = path_params.copy()

            # Add request body schema
            if meta["request_model"] and method in ("post", "put", "patch"):
                model = meta["request_model"]
                schema_name = model.__name__
                schemas[schema_name] = _clean_schema(model.model_json_schema())
                operation["requestBody"] = {
                    "required": True,
                    "content": {
                        "application/json": {
                            "schema": {"$ref": f"#/components/schemas/{schema_name}"}
                        }
                    },
                }

            # Add response schema
            if meta["response_model"]:
                model = meta["response_model"]
                schema_name = model.__name__
                schemas[schema_name] = _clean_schema(model.model_json_schema())
                operation["responses"]["200"] = {
                    "description": "Success",
                    "content": {
                        "application/json": {
                            "schema": {"$ref": f"#/components/schemas/{schema_name}"}
                        }
                    },
                }

            # Add additional responses
            for code, desc in meta["responses"].items():
                operation["responses"][str(code)] = {"description": desc}

            # Add to paths
            if openapi_path not in paths:
                paths[openapi_path] = {}
            paths[openapi_path][method] = operation

    # Build final spec
    spec: dict[str, Any] = {
        "openapi": "3.0.3",
        "info": {
            "title": title,
            "version": version,
            "description": description,
        },
        "paths": paths,
    }

    if tags_set:
        spec["tags"] = [{"name": tag} for tag in sorted(tags_set)]

    if schemas:
        spec["components"] = {"schemas": schemas}

    return spec


def _clean_schema(schema: dict[str, Any]) -> dict[str, Any]:
    """Clean Pydantic schema for OpenAPI compatibility."""
    # Remove $defs and flatten if needed
    schema.pop("$defs", None)
    schema.pop("title", None)
    return schema


# Swagger UI HTML template - uses string replacement to avoid Jinja2 conflicts
_SWAGGER_UI_TEMPLATE = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>__TITLE__ - API Docs</title>
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/swagger-ui-dist@5/swagger-ui.css">
    <style>
        body { margin: 0; padding: 0; }
        .swagger-ui .topbar { display: none; }
    </style>
</head>
<body>
    <div id="swagger-ui"></div>
    <script src="https://cdn.jsdelivr.net/npm/swagger-ui-dist@5/swagger-ui-bundle.js"></script>
    <script>
        window.onload = function() {
            SwaggerUIBundle({
                url: '/api/openapi.json',
                dom_id: '#swagger-ui',
                deepLinking: true,
                presets: [
                    SwaggerUIBundle.presets.apis,
                    SwaggerUIBundle.SwaggerUIStandalonePreset
                ],
                layout: "BaseLayout"
            });
        };
    </script>
</body>
</html>'''


def setup_openapi_routes(
    app: web.Application,
    title: str = "{{cookiecutter.app_name}} API",
    version: str = "1.0.0",
    description: str = "A modern async Python API built with aiohttp and SQLAlchemy 2.0",
) -> None:
    """
    Set up OpenAPI documentation routes.

    Adds:
    - GET /api/docs - Swagger UI
    - GET /api/openapi.json - OpenAPI JSON specification
    """
    async def openapi_json(request: web.Request) -> web.Response:
        """Serve the OpenAPI JSON specification."""
        import json
        spec = generate_openapi_spec(app, title=title, version=version, description=description)
        return web.Response(
            text=json.dumps(spec, indent=2),
            content_type="application/json",
        )

    async def swagger_ui(request: web.Request) -> web.Response:
        """Serve Swagger UI."""
        html = _SWAGGER_UI_TEMPLATE.replace("__TITLE__", title)
        return web.Response(text=html, content_type="text/html")

    app.router.add_get("/api/openapi.json", openapi_json)
    app.router.add_get("/api/docs", swagger_ui)
