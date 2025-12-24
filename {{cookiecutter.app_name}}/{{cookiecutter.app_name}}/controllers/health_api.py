"""
Health and Readiness API Controllers.

Provides endpoints for Kubernetes probes and monitoring.
"""
from datetime import UTC, datetime
from typing import Any

from aiohttp import web

from {{cookiecutter.app_name}} import __version__
from {{cookiecutter.app_name}}.controllers.base import BaseJsonApiController
from {{cookiecutter.app_name}}.core.database import db
from {{cookiecutter.app_name}}.core.logger import get_logger
from {{cookiecutter.app_name}}.core.redis import redis_client

_logger = get_logger()


class HealthApiController(BaseJsonApiController):
    """
    Health check controller for liveness probes.

    Returns basic application health status.
    """

    async def get(self, request: web.Request) -> web.Response:
        """
        Liveness probe endpoint.

        GET /api/-/health

        Returns 200 if the application is running.
        This is a lightweight check that should always succeed
        if the process is alive.
        """
        return self.json_response(body={
            "status": "healthy",
            "timestamp": datetime.now(UTC).isoformat(),
            "version": __version__,
        })


class ReadinessApiController(BaseJsonApiController):
    """
    Readiness check controller for readiness probes.

    Checks all dependencies (database, Redis, etc.) and returns
    whether the application is ready to receive traffic.
    """

    async def get(self, request: web.Request) -> web.Response:
        """
        Readiness probe endpoint.

        GET /api/-/ready

        Returns 200 if all dependencies are healthy,
        503 if any dependency is unhealthy.
        """
        checks: dict[str, dict[str, Any]] = {}
        all_healthy = True

        # Check database
        db_status = await self._check_database()
        checks["database"] = db_status
        if not db_status["healthy"]:
            all_healthy = False

        # Check Redis
        redis_status = await self._check_redis()
        checks["redis"] = redis_status
        if not redis_status["healthy"]:
            # Redis is optional, don't fail readiness
            _logger.warning("redis_unhealthy", error=redis_status.get("error"))

        status_code = 200 if all_healthy else 503
        status = "ready" if all_healthy else "not_ready"

        return self.json_response(
            body={
                "status": status,
                "timestamp": datetime.now(UTC).isoformat(),
                "version": __version__,
                "checks": checks,
            },
            status=status_code,
        )

    async def _check_database(self) -> dict[str, Any]:
        """Check database connectivity."""
        try:
            if db.engine is None:
                return {"healthy": False, "error": "Engine not initialized"}

            async with db.engine.connect() as conn:
                from sqlalchemy import text
                await conn.execute(text("SELECT 1"))

            return {"healthy": True, "latency_ms": 0}
        except Exception as e:
            _logger.error("database_health_check_failed", error=str(e))
            return {"healthy": False, "error": str(e)}

    async def _check_redis(self) -> dict[str, Any]:
        """Check Redis connectivity."""
        try:
            if redis_client.client is None:
                return {"healthy": False, "error": "Not connected"}

            await redis_client.client.ping()
            return {"healthy": True, "latency_ms": 0}
        except Exception as e:
            return {"healthy": False, "error": str(e)}


class LivenessApiController(BaseJsonApiController):
    """
    Simple liveness controller that just returns OK.

    Use this for basic Kubernetes liveness probes that should
    only fail if the process is truly dead.
    """

    async def get(self, request: web.Request) -> web.Response:
        """
        Simple liveness endpoint.

        GET /api/-/live

        Always returns 200 if the process is running.
        """
        return web.Response(text="OK", status=200)
