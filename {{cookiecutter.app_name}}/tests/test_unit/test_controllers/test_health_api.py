"""
Unit tests for Health API Controllers.

Tests liveness, readiness, and health check endpoints.
"""
from unittest.mock import AsyncMock, MagicMock, patch


class TestHealthApiController:
    """Tests for GET /api/-/health endpoint."""

    async def test_health_returns_200(self, client):
        """Test health endpoint returns 200."""
        response = await client.get("/api/-/health")
        assert response.status == 200

    async def test_health_returns_json(self, client):
        """Test health endpoint returns JSON response."""
        response = await client.get("/api/-/health")
        json_response = await response.json()

        assert isinstance(json_response, dict)
        assert "status" in json_response
        assert json_response["status"] == "healthy"
        assert "timestamp" in json_response
        assert "version" in json_response


class TestLivenessApiController:
    """Tests for GET /api/-/live endpoint."""

    async def test_liveness_returns_200(self, client):
        """Test liveness endpoint returns 200."""
        response = await client.get("/api/-/live")
        assert response.status == 200

    async def test_liveness_returns_ok(self, client):
        """Test liveness endpoint returns OK text."""
        response = await client.get("/api/-/live")
        text = await response.text()
        assert text == "OK"


class TestReadinessApiController:
    """Tests for GET /api/-/ready endpoint."""

    @patch('{{cookiecutter.app_name}}.controllers.health_api.db')
    @patch('{{cookiecutter.app_name}}.controllers.health_api.redis_client')
    async def test_readiness_returns_ready_when_deps_healthy(
        self, mock_redis, mock_db, client
    ):
        """Test readiness returns ready when all dependencies are healthy."""
        # Mock healthy database
        mock_engine = MagicMock()
        mock_conn = AsyncMock()
        mock_engine.connect = MagicMock(return_value=mock_conn)
        mock_conn.__aenter__ = AsyncMock(return_value=mock_conn)
        mock_conn.__aexit__ = AsyncMock(return_value=None)
        mock_conn.execute = AsyncMock()
        mock_db.engine = mock_engine

        # Mock healthy Redis
        mock_redis_client = AsyncMock()
        mock_redis_client.ping = AsyncMock()
        mock_redis.client = mock_redis_client

        response = await client.get("/api/-/ready")
        json_response = await response.json()

        assert response.status == 200
        assert json_response["status"] == "ready"
        assert "checks" in json_response

    @patch('{{cookiecutter.app_name}}.controllers.health_api.db')
    @patch('{{cookiecutter.app_name}}.controllers.health_api.redis_client')
    async def test_readiness_returns_not_ready_when_db_unhealthy(
        self, mock_redis, mock_db, client
    ):
        """Test readiness returns 503 when database is unhealthy."""
        # Mock unhealthy database
        mock_db.engine = None

        # Mock healthy Redis
        mock_redis.client = None

        response = await client.get("/api/-/ready")
        json_response = await response.json()

        assert response.status == 503
        assert json_response["status"] == "not_ready"


class TestMetricsEndpoint:
    """Tests for GET /metrics endpoint."""

    async def test_metrics_returns_200(self, client):
        """Test metrics endpoint returns 200."""
        response = await client.get("/metrics")
        assert response.status == 200

    async def test_metrics_returns_prometheus_format(self, client):
        """Test metrics endpoint returns Prometheus format."""
        response = await client.get("/metrics")
        content_type = response.headers.get("Content-Type", "")
        assert "text/plain" in content_type or "text/openmetrics-plain" in content_type

    async def test_metrics_contains_http_requests(self, client):
        """Test metrics contains HTTP request metrics."""
        # Make a request to generate metrics
        await client.get("/api/-/health")

        response = await client.get("/metrics")
        text = await response.text()

        assert "http_requests_total" in text
        assert "http_request_duration_seconds" in text
