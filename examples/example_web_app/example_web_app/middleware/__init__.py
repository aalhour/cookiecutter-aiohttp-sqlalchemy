"""
Middleware components for the aiohttp application.

This package contains all request/response middlewares:
- metrics: Prometheus metrics collection
- rate_limit: Redis-based rate limiting
- request_context: Request ID and logging context
- sentry: Error tracking with Sentry
- telemetry: OpenTelemetry distributed tracing
"""
from example_web_app.middleware.metrics import (
    metrics_middleware,
    setup_metrics,
    MetricsController,
    REQUEST_COUNT,
    REQUEST_LATENCY,
    REQUEST_IN_PROGRESS,
)
from example_web_app.middleware.rate_limit import (
    rate_limit_middleware,
    RateLimiter,
)
from example_web_app.middleware.request_context import (
    request_context_middleware,
)
from example_web_app.middleware.sentry import (
    sentry_middleware_factory,
)
from example_web_app.middleware.telemetry import (
    setup_telemetry,
    trace_middleware,
    get_tracer,
)

__all__ = [
    # Metrics
    "metrics_middleware",
    "setup_metrics",
    "MetricsController",
    "REQUEST_COUNT",
    "REQUEST_LATENCY",
    "REQUEST_IN_PROGRESS",
    # Rate limit
    "rate_limit_middleware",
    "RateLimiter",
    # Request context
    "request_context_middleware",
    # Sentry
    "sentry_middleware_factory",
    # Telemetry
    "setup_telemetry",
    "trace_middleware",
    "get_tracer",
]

