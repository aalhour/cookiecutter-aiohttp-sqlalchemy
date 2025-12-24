"""
Prometheus metrics for monitoring.

Provides request metrics, custom counters, and a /metrics endpoint.
"""
import time
from collections.abc import Callable

from aiohttp import web
from prometheus_client import (
    CONTENT_TYPE_LATEST,
    Counter,
    Gauge,
    Histogram,
    generate_latest,
)

from example_web_app.core.logger import get_logger

__all__ = [
    "setup_metrics",
    "metrics_middleware",
    "MetricsController",
    "REQUEST_COUNT",
    "REQUEST_LATENCY",
    "REQUEST_IN_PROGRESS",
    "DB_QUERY_COUNT",
    "DB_QUERY_LATENCY",
    "CACHE_HITS",
    "CACHE_MISSES",
    "WEBSOCKET_CONNECTIONS",
]

_logger = get_logger()

# Request metrics
REQUEST_COUNT = Counter(
    "http_requests_total",
    "Total HTTP requests",
    ["method", "endpoint", "status"],
)

REQUEST_LATENCY = Histogram(
    "http_request_duration_seconds",
    "HTTP request latency in seconds",
    ["method", "endpoint"],
    buckets=[0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0],
)

REQUEST_IN_PROGRESS = Gauge(
    "http_requests_in_progress",
    "HTTP requests currently in progress",
    ["method", "endpoint"],
)

# Database metrics
DB_QUERY_COUNT = Counter(
    "db_queries_total",
    "Total database queries",
    ["operation"],
)

DB_QUERY_LATENCY = Histogram(
    "db_query_duration_seconds",
    "Database query latency in seconds",
    ["operation"],
    buckets=[0.001, 0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0],
)

# Cache metrics
CACHE_HITS = Counter(
    "cache_hits_total",
    "Total cache hits",
    ["cache_name"],
)

CACHE_MISSES = Counter(
    "cache_misses_total",
    "Total cache misses",
    ["cache_name"],
)

# WebSocket metrics
WEBSOCKET_CONNECTIONS = Gauge(
    "websocket_connections_active",
    "Active WebSocket connections",
    ["room"],
)

# Application info
APP_INFO = Gauge(
    "app_info",
    "Application information",
    ["version"],
)


def setup_metrics(app: web.Application, version: str = "1.0.0") -> None:
    """
    Set up Prometheus metrics.

    Args:
        app: The aiohttp application
        version: Application version
    """
    APP_INFO.labels(version=version).set(1)
    _logger.info("metrics_initialized", version=version)


def metrics_middleware(exclude_paths: list[str] | None = None):
    """
    Create a metrics collection middleware.

    Args:
        exclude_paths: Paths to exclude from metrics (e.g., /metrics, /health)
    """
    exclude = set(exclude_paths or ["/metrics", "/api/-/health", "/api/-/ready"])

    @web.middleware
    async def middleware(request: web.Request, handler: Callable) -> web.Response:
        # Skip excluded paths
        if request.path in exclude:
            return await handler(request)

        # Normalize endpoint for labels (avoid high cardinality)
        endpoint = _normalize_path(request.path)
        method = request.method

        # Track in-progress requests
        REQUEST_IN_PROGRESS.labels(method=method, endpoint=endpoint).inc()
        start_time = time.perf_counter()

        try:
            response = await handler(request)
            status = str(response.status)
        except web.HTTPException as e:
            status = str(e.status)
            raise
        except Exception:
            status = "500"
            raise
        finally:
            # Record metrics
            duration = time.perf_counter() - start_time
            REQUEST_COUNT.labels(method=method, endpoint=endpoint, status=status).inc()
            REQUEST_LATENCY.labels(method=method, endpoint=endpoint).observe(duration)
            REQUEST_IN_PROGRESS.labels(method=method, endpoint=endpoint).dec()

        return response

    return middleware


def _normalize_path(path: str) -> str:
    """
    Normalize a path for use as a metric label.

    Replaces dynamic segments like IDs with placeholders to avoid
    high cardinality in metrics.
    """
    parts = path.split("/")
    normalized = []

    for part in parts:
        if not part:
            continue
        # Replace numeric IDs with placeholder
        if part.isdigit():
            normalized.append("{id}")
        # Replace UUIDs with placeholder
        elif len(part) == 36 and part.count("-") == 4:
            normalized.append("{uuid}")
        else:
            normalized.append(part)

    return "/" + "/".join(normalized) if normalized else "/"


class MetricsController:
    """
    Controller for Prometheus metrics endpoint.
    """

    async def get(self, request: web.Request) -> web.Response:
        """
        Prometheus metrics endpoint.

        GET /metrics
        """
        metrics = generate_latest()
        # CONTENT_TYPE_LATEST includes charset, but aiohttp wants them separate
        content_type = CONTENT_TYPE_LATEST.split(";")[0].strip()
        return web.Response(
            body=metrics,
            content_type=content_type,
            charset="utf-8",
        )

