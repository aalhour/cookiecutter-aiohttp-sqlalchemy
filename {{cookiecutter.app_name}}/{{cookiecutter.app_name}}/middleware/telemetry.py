"""
OpenTelemetry instrumentation for distributed tracing.

Provides automatic tracing for HTTP requests and database queries.
"""
import os
from collections.abc import Callable

from aiohttp import web

from {{cookiecutter.app_name}}.core.config import get_settings
from {{cookiecutter.app_name}}.core.logger import get_logger

__all__ = [
    "setup_telemetry",
    "trace_middleware",
    "get_tracer",
]

_logger = get_logger()

# Lazy imports to avoid import errors when opentelemetry is not configured
_tracer = None


def setup_telemetry(app: web.Application) -> None:
    """
    Set up OpenTelemetry instrumentation.

    Args:
        app: The aiohttp application
    """
    settings = get_settings()

    if not settings.telemetry.enabled:
        _logger.info("telemetry_disabled")
        return

    try:
        from opentelemetry import trace
        from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
        from opentelemetry.instrumentation.sqlalchemy import SQLAlchemyInstrumentor
        from opentelemetry.sdk.resources import Resource
        from opentelemetry.sdk.trace import TracerProvider
        from opentelemetry.sdk.trace.export import BatchSpanProcessor

        # Create resource with service info
        resource = Resource.create({
            "service.name": settings.telemetry.service_name,
            "service.version": "1.0.0",
            "deployment.environment": os.environ.get("ENVIRONMENT", "development"),
        })

        # Create tracer provider
        provider = TracerProvider(resource=resource)

        # Add OTLP exporter if endpoint is configured
        if settings.telemetry.otlp_endpoint:
            otlp_exporter = OTLPSpanExporter(
                endpoint=settings.telemetry.otlp_endpoint,
                insecure=settings.telemetry.otlp_insecure,
            )
            provider.add_span_processor(BatchSpanProcessor(otlp_exporter))
            _logger.info(
                "telemetry_otlp_configured",
                endpoint=settings.telemetry.otlp_endpoint,
            )

        # Set as global tracer provider
        trace.set_tracer_provider(provider)

        # Store tracer for use
        global _tracer
        _tracer = trace.get_tracer(__name__)

        # Instrument SQLAlchemy
        SQLAlchemyInstrumentor().instrument()

        _logger.info("telemetry_initialized", service=settings.telemetry.service_name)

    except ImportError as e:
        _logger.warning("telemetry_import_error", error=str(e))
    except Exception as e:
        _logger.error("telemetry_setup_error", error=str(e))


def get_tracer():
    """Get the OpenTelemetry tracer instance."""
    if _tracer is None:
        try:
            from opentelemetry import trace
            return trace.get_tracer(__name__)
        except ImportError:
            return None
    return _tracer


def trace_middleware():
    """
    Create a tracing middleware for aiohttp requests.

    Adds span for each request with method, path, and status.
    """

    @web.middleware
    async def middleware(request: web.Request, handler: Callable) -> web.Response:
        tracer = get_tracer()

        if tracer is None:
            return await handler(request)

        try:
            from opentelemetry import trace
            from opentelemetry.trace import SpanKind, Status, StatusCode

            with tracer.start_as_current_span(
                f"{request.method} {request.path}",
                kind=SpanKind.SERVER,
            ) as span:
                # Add request attributes
                span.set_attribute("http.method", request.method)
                span.set_attribute("http.url", str(request.url))
                span.set_attribute("http.route", request.path)
                span.set_attribute("http.scheme", request.scheme)

                if "X-Request-ID" in request.headers:
                    span.set_attribute("http.request_id", request.headers["X-Request-ID"])

                try:
                    response = await handler(request)
                    span.set_attribute("http.status_code", response.status)

                    if response.status >= 400:
                        span.set_status(Status(StatusCode.ERROR))
                    else:
                        span.set_status(Status(StatusCode.OK))

                    return response

                except Exception as e:
                    span.set_status(Status(StatusCode.ERROR, str(e)))
                    span.record_exception(e)
                    raise

        except ImportError:
            return await handler(request)

    return middleware

